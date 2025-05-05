from urllib.parse import urlparse
import base64
import re
import logging
from typing import List, Dict, Optional
import requests
from langchain.schema import HumanMessage
from langchain.schema.messages import SystemMessage
from langchain_openai import AzureChatOpenAI

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """Class to handle image fetching, analysis and text-image alignment checking."""
    
    def __init__(self, text_llm: AzureChatOpenAI, image_llm: AzureChatOpenAI, language: str = "vi"):
        """
        Initialize the ImageAnalyzer with LLM models.
        
        Args:
            text_llm: LLM for text analysis
            image_llm: LLM with vision capabilities for image analysis
            language: Output language (default: Vietnamese)
        """
        self.text_llm = text_llm
        self.image_llm = image_llm
        self.language = language
        self.image_extensions = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'svg', 'bmp']
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate if a string is a proper URL with scheme and domain."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and bool(parsed.scheme)
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False

    def get_base64_from_url(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch an image from URL and convert to base64.
        
        Args:
            url: The URL of the image
            timeout: Request timeout in seconds
            
        Returns:
            Base64 encoded image or None if failed
        """
        # Clean URL of whitespace and newline characters
        clean_url = url.strip().replace('\n', '').replace('\r', '').replace('%0A', '')
        
        if not self.is_valid_url(clean_url):
            logger.warning(f"Invalid URL format: {clean_url}")
            return None
        
        try:
            response = requests.get(clean_url, timeout=timeout, 
                                   headers={'User-Agent': 'Mozilla/5.0 (compatible; ImageAnalyzer/1.0)'})
            response.raise_for_status()
            
            # Check if content type is an image
            if 'image' not in response.headers.get('Content-Type', ''):
                logger.warning(f"URL does not contain an image: {clean_url}")
                return None
                
            return base64.b64encode(response.content).decode('utf-8')
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch image from {clean_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error processing {clean_url}: {e}")
            return None

    def describe_image(self, url: str) -> str:
        """
        Get a detailed description of an image using the vision-capable LLM.
        
        Args:
            url: URL of the image to analyze
            
        Returns:
            Detailed description of the image in the specified language
        """
        base64_image = self.get_base64_from_url(url)
        if not base64_image:
            return f"Image at URL {url} is unavailable or could not be fetched."

        messages = [
            SystemMessage(content=f"You are an expert in analyzing images and text in documents. Provide outputs in {self.language}."),
            HumanMessage(content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                },
                {
                    "type": "text",
                    "text": (
                        "Please analyze the provided image in detail. "
                        "Describe the content, layout, colors, objects, text, and any other relevant features. "
                        "If the image contains text, extract and summarize it. "
                        "Provide a comprehensive and structured description."
                    )
                }
            ])
        ]

        try:
            response = self.image_llm.invoke(messages)
            return str(response.content)
        except Exception as e:
            logger.error(f"Error describing image {url}: {e}")
            return f"Failed to analyze image at {url}: {str(e)}"

    def extract_image_urls(self, content: str) -> List[str]:
        """
        Extract image URLs from content.
        
        Args:
            content: HTML or text content to search for image URLs
            
        Returns:
            List of found image URLs
        """
        # Create pattern with all supported image extensions
        extensions = '|'.join(self.image_extensions)
        pattern = rf'https?://[^\s\'"]+\.(?:{extensions})'
        
        # Find all image URLs
        image_urls = re.findall(pattern, content, re.IGNORECASE)
        return image_urls

    def extract_alt_texts(self, content: str) -> Dict[str, str]:
        """
        Extract alt text attributes for images in markdown content.
        
        This function identifies images in markdown format and extracts their alt text
        and source URL. It handles both standard markdown image syntax and HTML img tags.
        
        Args:
            content (str): The markdown content to analyze
            
        Returns:
            Dict[str, str]: A dictionary mapping image URLs to their alt text
        """
        alt_texts = {}
        
        # Match markdown image pattern ![alt](url)
        md_img_pattern = r'!\[([^\]]*)\]\(([^"\)\s]+)(?:\s+"[^"]*")?\)'
        md_matches = re.findall(md_img_pattern, content)
        
        # Match HTML img tag pattern <img src="url" alt="alt text" />
        html_img_pattern = r'<img[^>]*src=["\'](.*?)["\'][^>]*alt=["\'](.*?)["\'][^>]*/?>'
        html_matches = re.findall(html_img_pattern, content)
        # Also match when alt comes before src
        html_img_pattern_alt_first = r'<img[^>]*alt=["\'](.*?)["\'][^>]*src=["\'](.*?)["\'][^>]*/?>'
        html_alt_first_matches = re.findall(html_img_pattern_alt_first, content)
        
        # Process markdown matches
        for alt, src in md_matches:
            # Clean and normalize URL
            src = src.strip()
            if self._is_image_file(src):
                alt_texts[src] = alt
        
        # Process HTML matches
        for src, alt in html_matches:
            if self._is_image_file(src):
                alt_texts[src] = alt
        
        # Process HTML matches where alt comes before src
        for alt, src in html_alt_first_matches:
            if self._is_image_file(src) and src not in alt_texts:
                alt_texts[src] = alt
                
        return alt_texts

    def _is_image_file(self, url: str) -> bool:
        """
        Check if the URL points to an image file.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if URL is an image file, False otherwise
        """
        # Handle URL parameters and fragments
        base_url = url.split('?')[0].split('#')[0]
        
        # Check if URL has a file extension that matches known image types
        return any(base_url.lower().endswith(ext) for ext in self.image_extensions)

    def check_image(self, content: str, window_size: int = 500) -> str:
        """
        Analyze image-text alignment in content.
        
        Args:
            content: The content to analyze
            window_size: Character window around images to consider as context
            
        Returns:
            Analysis of image-text alignment
        """
        image_urls = self.extract_image_urls(content)
        alt_texts = self.extract_alt_texts(content)
        
        if not image_urls:
            return "No image URLs found in the content."
            
        logger.info(f"Found {len(image_urls)} image URLs")
        
        # Copy original content for replacement
        processed_content = content
        
        # Process each image
        for idx, image_url in enumerate(image_urls):
            # Get image description
            logger.info(f"Processing image {idx+1}/{len(image_urls)}: {image_url}")
            description = self.describe_image(image_url)
            
            # Get alt text if available
            alt_text = alt_texts.get(image_url, "")
            if alt_text:
                description += f"\n\nExisting alt text: {alt_text}"
                
            # Create describe tag with index for easier reference
            describe_tag = f"<describe_image_{idx+1}>{description}</describe_image_{idx+1}>"
            
            # Find position of URL in content
            url_pos = processed_content.find(image_url)
            if url_pos == -1:
                logger.warning(f"URL not found in content: {image_url}")
                continue
                
            # Extract surrounding context
            start = max(0, url_pos - window_size)
            end = min(len(processed_content), url_pos + len(image_url) + window_size)
            context = processed_content[start:end]
            
            # Replace URL with description tag in the context
            context = context.replace(image_url, describe_tag)
            
            # Update the processed content
            processed_content = processed_content[:start] + context + processed_content[end:]

        # Create improved analysis prompt
        prompt = """
<prompt>
  <task>
    Bạn là một chuyên gia AI có khả năng đánh giá mức độ bổ trợ giữa hình ảnh và văn bản trong nội dung web. Nhiệm vụ của bạn là phân tích mức độ liên kết và hỗ trợ giữa các hình ảnh (được mô tả trong thẻ) và văn bản xung quanh, đồng thời đánh giá và cải thiện các thuộc tính alt text.
  </task>

  <input_format>
    Nội dung bao gồm đoạn văn bản với các mô tả hình ảnh được đánh dấu bằng thẻ <describe_image_n>...</describe_image_n> đã thay thế cho URL gốc của hình ảnh. Số n là chỉ số của hình ảnh trong nội dung.
  </input_format>

  <output_format>
    Đối với mỗi hình ảnh, hãy cung cấp phân tích như sau:

    ### Hình ảnh [index]:
    - **Mô tả tóm tắt:** (Tóm tắt ngắn gọn nội dung hình ảnh)
    - **Ngữ cảnh văn bản:** (Trích đoạn văn bản liên quan xung quanh hình ảnh)
    - **Mức độ bổ trợ:** [1-5]
    - **Phân tích:** (Giải thích chi tiết mối quan hệ giữa hình ảnh và văn bản)
    - **Đánh giá alt text:** [1-5] (nếu có)
    - **Đề xuất alt text:** (Đề xuất alt text tối ưu cho hình ảnh)
    - **Cải thiện khuyến nghị:** (Gợi ý cải thiện sự liên kết giữa hình ảnh và văn bản)
  </output_format>

  <scoring_criteria>
    - Mức độ bổ trợ:
      5: Hoàn hảo - Hình ảnh và văn bản bổ sung cho nhau một cách tối ưu, tạo giá trị gia tăng đáng kể
      4: Tốt - Hình ảnh và văn bản có mối liên hệ rõ ràng, hỗ trợ hiểu biết
      3: Đủ - Hình ảnh và văn bản liên quan nhưng không hỗ trợ sâu sắc
      2: Yếu - Có liên quan lỏng lẻo, không thực sự bổ sung
      1: Kém - Không liên quan hoặc gây hiểu nhầm
      
    - Đánh giá alt text:
      5: Mô tả đầy đủ, súc tích và chính xác nội dung và chức năng của hình ảnh
      4: Mô tả tốt nhưng có thể cải thiện
      3: Mô tả cơ bản nhưng thiếu chi tiết quan trọng
      2: Mô tả không đầy đủ hoặc quá chung chung
      1: Thiếu hoặc không liên quan đến nội dung hình ảnh
  </scoring_criteria>
</prompt>
        """

        # Submit for analysis
        messages = [
            SystemMessage(content=f"You are an expert in evaluating image-text alignment. Provide analysis in {self.language}."),
            HumanMessage(content=prompt + "\n\n" + processed_content)
        ]

        try:
            response = self.text_llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error in analyzing image-text alignment: {e}")
            return f"Failed to analyze image-text alignment: {str(e)}"

    def suggest_image_improvements(self, content: str) -> str:
        """
        Suggest improvements for images in the content based on the analysis.
        
        Args:
            content: The content with images to analyze
            
        Returns:
            Suggestions for improving images and their integration with text
        """
        # First, get the alignment analysis
        alignment_analysis = self.check_image_text_alignment(content)
        
        # Now ask for specific improvements
        improvement_prompt = f"""
Based on the following image-text alignment analysis, provide specific recommendations 
for improving the visual content strategy:

{alignment_analysis}

Please include:
1. Overall assessment of image usage in the content
2. Specific recommendations for each problematic image
3. General best practices for better image-text integration
4. Suggestions for alternative or additional images that would enhance the content
5. Recommendations for improving alt text across all images

Format your response as a comprehensive improvement plan, prioritizing changes 
that would have the greatest impact on user experience and accessibility.
"""

        messages = [
            SystemMessage(content=f"You are an expert in visual content strategy and accessibility. Provide recommendations in {self.language}."),
            HumanMessage(content=improvement_prompt)
        ]

        try:
            response = self.text_llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating improvement suggestions: {e}")
            return f"Failed to generate improvement suggestions: {str(e)}"
    
    def analyze_image_seo(self, content: str) -> str:
        """
        Analyze SEO aspects of images in the content.
        
        Args:
            content: The HTML or text content containing images
            
        Returns:
            Detailed SEO analysis of images
        """
        
        # Build prompt for SEO analysis
        seo_prompt = f"""
<prompt>
    <task>
        Bạn là một chuyên gia phân tích SEO cho hình ảnh trong nội dung web. Nhiệm vụ của bạn là đánh giá các yếu tố SEO của từng hình ảnh và đưa ra các đề xuất cải thiện.
    </task>

    <input_format>
        Đầu vào là 1 nội dung trang web có chứa các url hình ảnh và các thông tin liên quan.
        <input>
            {content}
        </input>
    </input_format>

    <output_format>
        ### Báo cáo SEO hình ảnh tổng quan:
        - **Số lượng hình ảnh được phân tích:** [số lượng]
        - **Điểm SEO trung bình:** [1-10]
        - **Tỷ lệ hình ảnh có alt text:** [%]
        - **Các vấn đề phổ biến:** [liệt kê]
        
        Cho mỗi hình ảnh:
        
        ### Hình ảnh [index]:
        - **URL:** [URL hình ảnh]
        - **Alt text:** [alt text nếu có, hoặc "Không có"]
        - **Tên file:** [tên file rút ra từ URL]
        - **Điểm SEO:** [1-10]
        
        **Phân tích:**
        1. **Alt text:** [đánh giá chất lượng alt text, độ dài, từ khóa]
        2. **Tên file:** [đánh giá tính tối ưu của tên file]
        3. **Ngữ cảnh:** [đánh giá sự phù hợp với nội dung xung quanh]
        4. **Mô tả hình ảnh:** [dựa vào phân tích nội dung hình ảnh từ mục <description>]
        
        **Đề xuất cải thiện:**
        - [Đề xuất alt text tối ưu hơn]
        - [Đề xuất tên file tối ưu hơn nếu cần]
        - [Các đề xuất khác về vị trí, kích thước, định dạng...]
    </output_format>

    <scoring_criteria>
        - Điểm SEO (1-10):
        10: Hoàn hảo - Tối ưu đầy đủ về alt text, tên file, ngữ cảnh và liên quan đến từ khóa
        8-9: Rất tốt - Hầu hết yếu tố đã tối ưu nhưng còn cải thiện nhỏ
        6-7: Tốt - Cơ bản được tối ưu nhưng cần cải thiện đáng kể
        4-5: Trung bình - Nhiều yếu tố chưa tối ưu
        2-3: Yếu - Hầu hết yếu tố SEO chưa được áp dụng
        1: Rất kém - Không có bất kỳ tối ưu SEO nào
    </scoring_criteria>
</prompt>
        """
        
        
        
        # Submit for SEO analysis
        messages = [
            SystemMessage(content=f"Bạn là chuyên gia phân tích SEO cho hình ảnh. Cung cấp phân tích chi tiết bằng {self.language}."),
            HumanMessage(content=seo_prompt)
        ]

        try:
            response = self.text_llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Lỗi khi phân tích SEO hình ảnh: {e}")
            return f"Không thể hoàn thành phân tích SEO hình ảnh: {str(e)}"
    
    def check_size_image(self, content: str) -> str:
        prompt = f"""
    Kiểm tra chiều rộng của các ảnh trong nội dung sau có phải là 1050 hay không, trả về kết quả dạng check list (dùng biểu tượng Yes: ✅,No: ❌) mỗi ảnh 1 dòng.
    Nội dung: {content} 
"""
        
        response = self.text_llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def check_image_full_report(self, content: str) -> str:
        """
        Generate a comprehensive report on images including alignment with text and SEO aspects.
        
        Args:
            content: The HTML or text content containing images
            
        Returns:
            Comprehensive analysis of images
        """
        alignment_analysis = self.check_image(content)
        seo_analysis = self.analyze_image_seo(content)
        check_size = self.check_size_image(content)
        
        report_prompt = f"""
    Dựa trên hai phân tích sau đây về hình ảnh trong nội dung web:

    1. Phân tích mối quan hệ hình ảnh - văn bản:
    {alignment_analysis}

    2. Phân tích SEO hình ảnh:
    {seo_analysis}

    3. Kiểm tra chiều rộng hình ảnh:
    {check_size}

    Hãy tổng hợp thành một báo cáo toàn diện về hình ảnh trong nội dung, được trình bày hoàn toàn dưới dạng danh sách có đánh số hoặc gạch đầu dòng. Không sử dụng bảng hoặc định dạng khác. Báo cáo cần bao gồm:

    1. Tổng quan về chất lượng và hiệu quả của hình ảnh:
       - Liệt kê từng điểm đánh giá chất lượng hình ảnh
       - Liệt kê các yếu tố về hiệu quả sử dụng hình ảnh

    2. Những điểm mạnh cần duy trì:
       - Liệt kê từng điểm mạnh của việc sử dụng hình ảnh
       - Mỗi điểm mạnh cần được trình bày riêng biệt trên một dòng

    3. Các vấn đề chính cần khắc phục:
       - Liệt kê từng vấn đề theo thứ tự ưu tiên
       - Mỗi vấn đề được trình bày trên một dòng riêng biệt

    4. Kế hoạch hành động ưu tiên để cải thiện:
       - Liệt kê từng hành động cần thực hiện theo thứ tự ưu tiên
       - Mỗi hành động được trình bày trên một dòng riêng biệt

    5. Dự đoán tác động của những cải thiện:
       - Liệt kê các tác động dự kiến đối với SEO
       - Liệt kê các tác động dự kiến đối với trải nghiệm người dùng

    Đối với từng hình ảnh cụ thể, hãy đánh giá bằng danh sách riêng biệt, như sau:
    
    ĐÁNH GIÁ HÌNH ẢNH [tên/ID hình ảnh]:
    - Điểm mạnh: [liệt kê từng điểm mạnh]
    - Vấn đề: [liệt kê từng vấn đề]
    - Đề xuất cải thiện: [liệt kê từng đề xuất]
    
    Đảm bảo không sử dụng bảng, ma trận hoặc bất kỳ định dạng nào khác ngoài danh sách đơn giản có đánh số hoặc gạch đầu dòng.
    """
        
        # Submit for comprehensive analysis
        messages = [
            SystemMessage(content=f"Bạn là chuyên gia phân tích nội dung và SEO. Cung cấp báo cáo chuyên sâu bằng {self.language}."),
            HumanMessage(content=report_prompt)
        ]

        try:
            response = self.text_llm.invoke(messages)
            return f"{response.content}\n\n##---CHI TIẾT---\n{alignment_analysis}\n{seo_analysis}\n{check_size}"
        except Exception as e:
            logger.error(f"Lỗi khi tạo báo cáo tổng hợp: {e}")
            return f"Không thể tạo báo cáo tổng hợp về hình ảnh: {str(e)}"
        
def check_image(text_llm, image_llm, content: str) -> str:
    image_analyzer = ImageAnalyzer(text_llm, image_llm)
    res = image_analyzer
    return image_analyzer.check_image_full_report(content)

if __name__ == "__main__":
    from langchain_openai import AzureChatOpenAI
    from dotenv import load_dotenv
    import os

    load_dotenv()

    image_llm = AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            model="gpt-4o-mini",
            api_version="2024-08-01-preview",
            temperature=0.7,
            max_tokens=16000
        )

    text_llm = AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            model="o3-mini",
            api_version="2024-12-01-preview",
        )
    
    content = "![Cover Image][width=1023,height=574][width=1023,height=574](https://statics.gemxresearch.com/images/2025/04/25/150501/real-world-assets-rwa-la-gi-ung-dung-cua-rwa-trong-defi.jpg) # Ứng dụng của RWA trong DeFi ## **Tổng quan&nbsp;** Thời gian qua, từ khóa [“**RWA**” – **Real World Assets**][rel=NO](https://gfiresearch.net/post/real-world-assets-rwa-la-gi-ung-dung-cua-rwa-trong-defi) (tài sản trong thế giới thực) đang được nhắc đến nhiều trên các nền tảng truyền thông. Đây được xem là xu hướng mới giúp thúc đẩy sự phát triển của thị trường DeFi sau một thời gian không có nhiều biến động.Vậy RWA là gì và có thể được ứng dụng như thế nào trong thị trường DeFi? Tất cả sẽ được tổng hợp trong bài viết dưới đây của [GFI Research][rel=NO](https://gfiresearch.net/). ## **Vì sao cần đưa RWA lên blockchain?&nbsp;** ### Thực trạng ảm đạm của thị trường DeFi&nbsp; Thị trường **DeFi** đã phát triển mạnh từ đầu năm 2020 và đạt mốc TVL hơn 180 tỷ USD vào cuối năm 2021. Kể từ đó, cùng với đà downtrend của thị trường, giá trị tài sản được khóa (TVL) trên các giao thức DeFi đã sụt giảm mạnh, chỉ còn dưới 50 tỷ USD.![][width=1050,height=449](https://statics.gemxresearch.com/images/2025/04/24/105916/thuc-trang-am-dam-cua-thi-truong-defi.jpg)  Vốn là trụ cột về tiến bộ công nghệ và là động lực phát triển của cả ngành blockchain, tuy nhiên hiện nay, DeFi vẫn mắc kẹt trong những mô hình tokenomics nghèo nàn với tỉ lệ lạm phát token cao.Một số token giảm hơn 90% giá trị, thậm chí biến mất khỏi thị trường, kéo theo lợi nhuận cho người dùng cũng giảm đáng kể. Lợi suất từ DeFi giờ chỉ còn tương đương với TradFi (Traditional Finance – tài chính truyền thống).Dễ thấy rằng TradFi cung cấp một mô hình đầu tư ít rủi ro hơn nhiều so với DeFi. Vậy khi lãi suất giữa hai mảng là như nhau, người dùng DeFi sẽ dần rút lui và trở về với TradFi. Thực trạng này đòi hỏi một nguồn lợi suất mới để vực dậy DeFi, và Real World Assets chính là câu trả lời. ### Động lực mới từ RWA&nbsp; Hiện nay, Real World Assets đang đóng góp một phần rất lớn vào giá trị của nền tài chính toàn cầu. Trong đó, thị trường nợ (với dòng tiền cố định) đã có giá trị khoảng 127 nghìn tỷ USD, thị trường bất động sản có giá trị khoảng 362 nghìn tỷ USD, và vốn hóa thị trường vàng là khoảng 11 nghìn tỷ USD.Trong khi đó, với TVL chỉ 50 tỷ USD, thị trường DeFi giống như một người tí hon so với vốn hóa của RWA. Nếu đưa được RWA lên blockchain, thị trường DeFi sẽ nhận được một dòng tài sản dồi dào những mô hình lợi nhuận đa dạng hơn, từ đó thúc đẩy tăng trưởng. ### DeFi mở ra tiềm năng khổng lồ cho RWA&nbsp; Không chỉ là bên được lợi từ Real World Assets, DeFi cũng giúp tạo ra một mô hình thị trường hiệu quả hơn, đặc biệt trong bối cảnh hiệu suất của TradFi đang dần bão hòa.TradFi đã phải phụ thuộc vào hệ thống trung gian từ ngày mới ra đời. Hệ thống trung gian gồm người môi giới, các hoạt động xác thực danh tính, và các quy định. Hệ thống này đã phần nào đảm bảo an toàn cho các giao dịch, nhưng đi kèm với đó là những hạn chế về hiệu quả sử dụng vốn.Theo Báo cáo ổn định tài chính toàn cầu 2022 của Quỹ Tiền tệ Quốc tế (IMF), TradFi kém hiệu quả vì người tham gia thị trường phải trả phí cho bên trung gian (gồm phí lao động và phí quản lý hệ thống).Ngoài ra, tài sản người dùng cũng bị kiểm soát bởi một bên thứ ba và đôi khi người dùng còn bị chặn khỏi hệ thống. Các mô hình DeFi sẽ giúp loại bỏ những hạn chế này này.Bên cạnh việc loại bỏ hệ thống trung gian, việc áp dụng DeFi vào RWA cũng giúp người dùng dễ dàng đa dạng hóa danh mục đầu tư thông qua các token. Thanh khoản cũng nhanh chóng với các mô hình AMM giúp người dùng ngay lập tức hoàn thành giao dịch.Đây là lợi ích cực kỳ lớn đối với những người đã quen với giao dịch chứng khoán. Nhà đầu tư chứng khoán thường phải liên hệ với công ty môi giới để giao dịch, và các giao dịch thường có độ trễ (như T+1, T+3).Một lợi ích cuối cùng của DeFi cho RWA chính là sự minh bạch của sổ cái blockchain, giúp người dùng quan sát được luồng giao dịch, từ đó đánh giá được tình hình thị trường. Những thông tin này thường bị giấu kín trong TradFi. ## **Ứng dụng của Real World Assets trong DeFi&nbsp;** Vậy khi Real World Assets được đưa lên blockchain, chúng sẽ được sử dụng như thế nào trong DeFi? Hiện nay, RWA có 3 ứng dụng chính trong DeFi:- Sử dụng làm **stablecoin**. - Tạo ra **synthetic token** (token tổng hợp). - Sử dụng làm tài sản trong các giao thức **lending**. ### Stablecoin Stablecoin là ví dụ hoàn hảo nhất của việc sử dụng RWA trong DeFi. USDT và USDC là 2 đồng stablecoin thường xuyên nằm trong top 5 token crypto hàng đầu theo vốn hóa thị trường, với tổng vốn hóa của chúng hiện đang ở mức hơn 110 tỷ USD. Điểm chung của cả hai là đều được đảm bảo bởi các tài sản thực như USD và trái phiếu.Hiện nay, USDC được đảm bảo peg 1:1 với USD nhờ kho tài sản dự trữ gồm 8,1 tỷ USD tiền mặt và 29 tỷ USD trái phiếu Kho bạc Hoa Kỳ. Tương tự, hơn 80% tài sản dự trữ của USDT là tiền mặt và trái phiếu Kho bạc, còn lại là trái phiếu doanh nghiệp, tiền cho vay và các khoản đầu tư khác.![][width=1050,height=993](https://statics.gemxresearch.com/images/2025/04/24/105957/usdc-duoc-dam-bao-boi-tien-mat-va-trai-phieu-kho-bac-hoa-ky.jpg)  Với tính chất này, các stablecoin là tài sản quan trọng của DeFi, hỗ trợ luân chuyển giá trị giữa thế giới thực và blockchain, cũng như là một tài sản trung gian để trú ẩn sự biến động của thị trường. ### Synthetic token&nbsp; Synthetic token hỗ trợ giao dịch on-chain cho các sản phẩm tài chính phái sinh liên quan đến tiền tệ, cổ phiếu và hàng hóa. Một nền tảng giao dịch synthetic token rất phổ biến là **Synthetix (SNX)** đã đạt mốc TVL gần 3 tỷ USD vào năm 2021.![][width=1050,height=393](https://statics.gemxresearch.com/images/2025/04/24/110017/tvl-cua-synthetix-tung-dat-hon-3-ty-usd.jpg)  Synthetic token có nhiều ứng dụng thú vị. Chẳng hạn, người nắm giữ tài sản thực như bất động sản có thể chứng khoán hóa dòng tiền từ hoạt động cho thuê, sau đó tokenize chứng khoán đó thành synthetic token để giao dịch trên DeFi. ### Lending&nbsp; Một số nền tảng lending như **Goldfinch**, **Maple Finance** hay **Centrifuge** giúp hỗ trợ vốn vay cho các doanh nghiệp trong thế giới thực. Các nền tảng này yêu cầu doanh nghiệp cung cấp các bằng chứng về tài sản và doanh thu, từ đó nhà đầu tư có thể cho các doanh nghiệp vay tiền một cách phi tập trung.Mô hình này cung cấp lợi nhuận tương đối ổn định và không chịu sự biến động của thị trường tiền điện tử. ## **Kết luận&nbsp;** **Real World Assets** là những tài sản ở thế giới thực được đưa lên blockchain nhằm tạo ra nguồn tài sản mới cho DeFi. DeFi cũng giúp người sở hữu RWA tối ưu hiệu quả sử dụng vốn so với TradFi.Một số ứng dụng nổi bật của RWA trong DeFi là stablecoin, synthetic token và lending. Đây chỉ là các ứng dụng đơn giản, do đó lĩnh vực này còn rất nhiều tiềm năng phát triển trong tương lai.Tuy nhiên, cũng phải để ý một số thách thức đặt ra cho RWA như **vấn đề định giá** và **xác thực cho tài sản**. Những bài viết tiếp theo của GFI Research sẽ đào sâu hơn về chủ đề này. ~~~metadata undefined: undefined undefined: undefined undefined: undefined Excerpt: undefined: undefined undefined: undefined Meta description: RWA” – Real World Assets (tài sản trong thế giới thực) thúc đẩy sự phát triển của thị trường DeFi sau một thời gian không có nhiều biến động. postUrl: ung-dung-cua-rwa-trong-defi ~~~"

    # imageanalyzer = ImageAnalyzer(text_llm, image_llm)
    # print(imageanalyzer.check_size_image(content))

    print(check_image(text_llm, image_llm, content))