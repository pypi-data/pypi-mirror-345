# Standard library imports
import os
import re
import logging

# Third-party imports
import requests
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

# LangChain and LangGraph imports
from langchain_core.tools import Tool
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from playwright.sync_api import sync_playwright, Browser

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

"""
This module provides functionality to validate claims in blog articles using 
LangChain and web search tools. It uses a combination of SearxNG search and 
Playwright web scraping to gather evidence and verify statements.
"""

def searxng_search(query: str, base_url: str) -> str:
    """
    Performs a web search using SearxNG API and returns formatted results.
    
    Args:
        query (str): The search query string
        
    Returns:
        str: Formatted search results containing title, URL and content
        
    Raises:
        Exception: If the search request fails
    """
    try:
        response = requests.get(
            f"{base_url}/search",
            params={"q": query, "format": "json", "language": "en", "categories": "general"},
            timeout=10
        )
        response.raise_for_status()
        results = response.json().get("results", [])[:5]

        if not results:
            return "No relevant results found."

        res = []
        for result in results:
            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")
            res.append(f"Title: {title}\nURL: {url}\nContent: {content}")

        return "\n\n".join(res)

    except Exception as e:
        return f"Error during search: {e}"
    
def draw_web_content_playwright(browser: Browser, url: str) -> str:
    """
    Extracts content from a webpage using Playwright.
    
    Args:
        browser (Browser): Playwright browser instance
        url (str): URL to scrape
        
    Returns:
        str: Text content of the webpage
        
    Raises:
        Exception: If webpage access or content extraction fails
    """
    try:
        with sync_playwright() as p:
            page = browser.new_page()
            page.goto(url)
            text_content = page.evaluate("document.body")
            return text_content
    except Exception as e:
        return f"Error: {str(e)}"

def is_url(text: str) -> bool:
    """
    Checks if a string matches URL pattern.
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if text is a URL, False otherwise
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return bool(url_pattern.match(text))

def extract_url(text: str) -> str:
    """
    Extracts the first URL from a text string.
    
    Args:
        text (str): Text containing URLs
        
    Returns:
        str: First URL found or empty string if none found
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    urls = url_pattern.findall(text)
    return urls[0] if urls else ""

def format_fact_check_results(results: list[dict]) -> str:
    """
    Formats fact checking results into a readable bulleted list string.
    
    Args:
        results (list[dict]): List of fact check results with claim, conclusion, source and explanation
        
    Returns:
        str: Formatted string with bullet points for each result
    """
    if not results:
        return "No fact check results available."
        
    formatted = "Fact Check Results:\n\n"

    for i in range(len(results)):
        result = results[i]
        formatted += f"   Phát biểu: {result['claim']}\n"
        formatted += f"   Kết luận: {result['conclusion']}\n"
        formatted += f"   Nguồn tin: {result['source']}\n" 
        formatted += f"   Giải thích: {result['explanation']}\n\n"
    
    return formatted

def check_fact(llm: AzureChatOpenAI, text: str, base_url: str) -> list[dict]:
    """
    Analyzes text for claims and verifies them using AI and search tools.
    
    Uses a state machine architecture with LangGraph to:
    1. Extract claims from input text
    2. Verify each claim using web search and AI analysis
    3. Build a chain of tools including SearxNG search and web content extraction
    
    Args:
        llm (AzureChatOpenAI): Language model instance
        text (str): Input text to analyze
        
    Returns:
        list[dict]: List of verified claims with their conclusions, sources and explanations
    """

    def searxng_search_tool(query: str) -> str:
        return searxng_search(base_url, query)

    # Define search tools
    search_tool = Tool(
        name="SearxNG_Search",  
        func=searxng_search_tool,
        description="Use this tool to search for information on the web. Input should be a search query.",
    )
    
    draw_tool = Tool(
        name="draw_web_content_playwright",
        func=draw_web_content_playwright,
        description="Use this tool to extract full content from a webpage. Input should be a URL.",
    )

    # State and graph setup
    class State(TypedDict):
        messages: Annotated[list, add_messages]

    graph_builder = StateGraph(State)

    def chatbot(state: State):
        logger.info("Processing message in chatbot node")
        response = llm.invoke(state["messages"])
        logger.info(f"LLM response received: {response.content[:100]}...")
        return {"messages": [response]}

    def should_draw(state: State) -> bool:
        last_message = state["messages"][-1].content
        should_draw_result = "No relevant results found" in last_message and is_url(extract_url(last_message))
        logger.debug(f"Should draw check: {should_draw_result}")
        if should_draw_result:
            logger.info(f"URL to be drawn: {extract_url(last_message)}")
        return should_draw_result

    def route(state: State):
        last_message = state["messages"][-1].content
        route_decision = None
        if should_draw(state):
            route_decision = "draw"
        elif "tool" in last_message.lower():
            route_decision = "search"
        else:
            route_decision = END
        logger.info(f"Routing decision: {route_decision}")
        return route_decision

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("search", ToolNode(tools=[search_tool]))
    graph_builder.add_node("draw", ToolNode(tools=[draw_tool]))

    # Add edges
    graph_builder.add_conditional_edges("chatbot", route, {
        "search": "search",
        "draw": "draw",
        END: END
    })
    graph_builder.add_edge("search", "chatbot")
    graph_builder.add_edge("draw", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    graph_builder.set_entry_point("chatbot")
    graph = graph_builder.compile()

    claims = llm.invoke(f"""
Bạn là chuyên gia trong việc tách các phát biểu cần xác thực từ trong các bài phân tích. 

Nhiệm vụ của bạn:
1. Đọc kỹ bài phân tích dưới đây
2. Xác định các ý/phát biểu cần được kiểm chứng (không nhất thiết phải theo từng câu riêng lẻ, vì một ý có thể được diễn đạt qua 2-3 câu)
3. Liệt kê các phát biểu cần xác thực theo từng dòng
4. CHỈ trả về danh sách các phát biểu, không đưa ra bất kỳ giải thích, bình luận hay nội dung nào khác

Bài phân tích cần xử lý:
{text}
""").content.split("\n")
    logger.info(f"Extracted {len(claims)} claims to verify")

    results = []
    for i in range(len(claims)):
        claim = claims[i]
        logger.info(f"Processing claim {i+1}/{len(claims)}: {claim[:100]}...")
        prompt = (
            f"Hãy kiểm tra phát biểu sau là ĐÚNG hay SAI dựa trên thông tin tìm kiếm từ công cụ.\n"
            f"Phát biểu: \"{claim}\"\n"
            f"Trả lời theo định dạng:\n"
            f"Kết luận: ✅ Đúng/❌ Sai/⚠️ Không xác định\n"
            f"Nguồn tin: <đường link tìm kiếm>\n"
            f"Giải thích: <giải thích chi tiết>"
        )

        final_answer = None
        for event in graph.stream({"messages": [{"role": "user", "content": prompt}]}):
            for value in event.values():
                final_answer = value["messages"][-1].content

        if final_answer:
            lines = final_answer.strip().split("\n")
            conclusion = next((line for line in lines if "Kết luận" in line), "Kết luận: Không rõ")
            source_line = next((line for line in lines if "Nguồn tin" in line), "Nguồn tin: Không rõ")
            explanation = next((line for line in lines if "Giải thích" in line), "Giải thích: Không có.")
            results.append({
                "claim": claim,
                "conclusion": conclusion.replace("Kết luận:", "").strip(),
                "source": source_line.replace("Nguồn tin:", "").strip(),
                "explanation": explanation.replace("Giải thích:", "").strip()
            })
        else:
            results.append({
                "claim": claim,
                "conclusion": "Không rõ",
                "source": "Không rõ",
                "explanation": "LLM không phản hồi được."
            })
    logger.info("Fact checking completed")
    return format_fact_check_results(results)

if __name__ == "__main__":
    
    text = "![Cover Image](https://statics.gemxresearch.com/images/2025/04/11/154715/capwheel-series-pancake-swap.jpg)\n\n# CapWheel Series: PancakeSwap và token $CAKE\n\n **CapWheel Series** là chuỗi bài viết chuyên sâu [phân tích](https://gfiresearch.net/analysis) cách các dự án thiết kế mô hình Tokenomics và sản phẩm để khai thác giá trị cho token của họ. Mục tiêu của series này là cung cấp cái nhìn sâu sắc về giá trị nội tại của token, giúp đánh giá tiềm năng dài hạn của các dự án, thay vì chỉ chú trọng vào biến động ngắn hạn trên thị trường. CapWheel Series tập trung vào việc các dự án xây dựng cơ chế tích lũy giá trị qua các mô hình Tokenomics, thay vì phụ thuộc vào các yếu tố bên ngoài như tình hình thị trường chung hay sự tác động của các yếu tố đầu cơ. \n ## Điểm nổi bật\n\n- Pancake nổi bật so với các sàn DEX khác nhờ hệ sinh thái đa dạng, tích hợp nhiều sản phẩm nhằm thúc đẩy cơ chế Burn trong mô hình Mint &amp; Burn của CAKE. Tuy nhiên, phần lớn lượng CAKE được Burn vẫn đến từ các hoạt động DEX, trong khi các sản phẩm khác chỉ đóng góp khoảng 11% vào tổng lượng Burn.\n\n\n- Đề xuất loại bỏ veCAKE được đưa ra với mục tiêu kiểm soát nguồn cung hiệu quả hơn, nhưng lại vấp phải tranh cãi gay gắt về tính phi tập trung. Pancake bị nghi ngờ đã có những động thái không minh bạch nhằm giảm sức ép từ các Liquid Wrappers trước khi đề xuất được đưa vào biểu quyết, làm dấy lên nhiều lo ngại trong cộng đồng.\n\n\n \n ## Tổng quan về PancakeSwap\n\nPancakeSwap hiện là sàn giao dịch phi tập trung (DEX) hàng đầu trên BNB Smart Chain, ghi dấu ấn với khối lượng giao dịch vượt trội, khẳng định vị thế tiên phong trong thị trường tài chính phi tập trung (DeFi). Với sự đổi mới không ngừng, PancakeSwap mang đến một hệ sinh thái đa dạng, tối ưu hóa trải nghiệm cho người dùng, nhà phát triển và nhà cung cấp thanh khoản.\n\nCác \n\nsản phẩm \n\ntrong hệ sinh thái PancakeSwap\n\nPancakeSwap cung cấp một loạt sản phẩm tiên tiến, được thiết kế để đáp ứng nhu cầu đa dạng của cộng đồng DeFi. Dưới đây là những điểm nhấn quan trọng:\n\nAMM Swap\n\nKế thừa từ Uniswap, PancakeSwap không chỉ tái hiện đầy đủ các tính năng cốt lõi mà còn nâng tầm với phiên bản V4, mang đến những cải tiến đột phá:\n\n- Hooks: Các hợp đồng thông minh bên ngoài cho phép tùy chỉnh linh hoạt các hồ thanh khoản, hỗ trợ phí động (thấp đến 0%), công cụ giao dịch nâng cao (lệnh giới hạn, chốt lời, TWAMM, hoàn phí), và tạo doanh thu cho nhà phát triển, thúc đẩy đổi mới.\n\n\n- Đa dạng Liquidity Pool tích hợp liền mạch với HOOKS như Concentrated Liquidity Automated Market Maker (CLAMM), Liquidity Book AMM (LBAMM) hay các Liquidity Pool có thiết kế mở, sẵn sàng cho các mô hình AMM mới, đáp ứng nhu cầu thị trường.\n\n\n- Donate: Khuyến khích nhà cung cấp thanh khoản trong phạm vi giá phù hợp, tăng lợi nhuận và sự tham gia.\n\n\n- Singleton: Gộp tất cả hồ thanh khoản vào một hợp đồng, giảm 99% chi phí tạo hồ và tối ưu gas cho giao dịch đa bước.\n\n\n- Flash Accounting: Tối ưu gas bằng cách tính toán số dư ròng và thanh toán tập trung, giảm chi phí so với mô hình cũ.\n\n\n- ERC-6909: Chuẩn đa token, quản lý token thay thế và không thay thế trong một hợp đồng, tăng hiệu quả, giảm chi phí.\n\n\n- Token Gas Gốc: Hỗ trợ giao dịch với token gas gốc, giảm chi phí và cải thiện trải nghiệm người dùng.\n\n\n- Mã Nguồn Mở: Khuyến khích nhà phát triển đổi mới và hợp tác thông qua giấy phép mở.\n\n\n- Chương trình Nhà phát triển: Quỹ 500.000 USD hỗ trợ chiến dịch tăng trưởng, hackathon, đại sứ phát triển, và tài trợ CAKE, thúc đẩy sáng tạo cộng đồng.\n\n\nEarn\n\n**Add LP &amp; Farming**Tương tự như các AMM Dex khác, người dùng có thể add liquid vào các liquidity pools ở trong Pancake và stake LP để farm ra CAKE từ lượng Emission.\n\n![](https://statics.gemxresearch.com/images/2025/04/11/154948/ADD-LP.png)  **Staking &amp; Syrup Pool**Syrup Pool là một sản phẩm staking của PancakeSwap, cho phép người dùng khóa CAKE hoặc các token khác để nhận phần thưởng dưới dạng CAKE hoặc token từ các dự án đối tác. Đây là cách đơn giản để kiếm lợi nhuận thụ động, đồng thời hỗ trợ hệ sinh thái PancakeSwap. Có hai loại pool chính:\n\n- CAKE Pool: Stake CAKE để nhận CAKE hoặc iCAKE (dùng cho IFO), chia thành Flexible Staking (rút bất kỳ lúc nào, APR thấp hơn) và Fixed-Term Staking (khóa cố định 1-52 tuần, APR cao hơn, tự động gia hạn trừ khi rút).\n\n\n- Non-CAKE Pool: Stake token từ dự án đối tác để nhận phần thưởng là token dự án đó hoặc CAKE, thường có thời hạn cố định.\n\n\n![](https://statics.gemxresearch.com/images/2025/04/11/152622/Syrup Pool.png)  **IFO**Initial Farm Offering (IFO) của PancakeSwap là một cơ hội độc đáo để người dùng tiếp cận sớm các token mới, tương tự IDO nhưng được thiết kế riêng với sự tham gia thông qua CAKE, mang đến tiềm năng lợi nhuận hấp dẫn.\n\nĐể tham gia, người dùng cần khóa CAKE trong để nhận veCAKE, từ đó tạo ra iCAKE – chỉ số quyết định hạn mức tham gia IFO, với số lượng và thời gian khóa càng lớn\n\n thì iCAKE càng cao, mở rộng cơ hội trong Public Sale. Ngoài ra, cần tạo NFT Profile với một khoản phí nhỏ bằng CAKE, được sử dụng để đốt, góp phần giảm nguồn cung token và tăng giá trị dài hạn cho hệ sinh thái\n\n![](https://statics.gemxresearch.com/images/2025/04/11/152744/ifo.png)  Play**Prediction**Prediction của PancakeSwap là một trò chơi dự đoán phi tập trung, đơn giản và thú vị, cho phép người dùng dự đoán giá BNBUSD, CAKEUSD hoặc ETHUSD sẽ tăng (UP) hay giảm (DOWN) trong các vòng kéo dài 5 phút (hoặc 10 phút trên zkSync). Người chơi đặt cược bằng BNB, CAKE hoặc ETH tùy thuộc vào thị trường, và nếu dự đoán đúng, họ chia sẻ quỹ thưởng của vòng.\n\n![](https://statics.gemxresearch.com/images/2025/04/11/152822/prediction.png)  **Lottery**Lottery của PancakeSwap là trò chơi minh bạch, dễ tham gia, cho phép người dùng mua vé bằng CAKE (giá ~5 USD/vé, tối đa 100 vé/lần) để có cơ hội nhận thưởng lớn. Người chơi chọn 6 số, khớp càng nhiều số với kết quả ngẫu nhiên (dùng Chainlink VRF) càng nhận thưởng cao, từ giải nhỏ đến độc đắc. Tổng giải thưởng gồm CAKE từ vé bán và 10,000 CAKE bổ sung mỗi 2 ngày. Mua nhiều vé được chiết khấu, nhưng tăng nhẹ phí giao dịch. Một phần CAKE được đốt để giảm phát. Mỗi vòng kéo dài 12 giờ, vé không hoàn lại, kết quả kiểm tra thủ công. Lottery v2 tăng số khớp từ 4 lên 6, nâng cơ hội trúng giải nhỏ và tích lũy quỹ lớn hơn.\n\n![](https://statics.gemxresearch.com/images/2025/04/11/152856/lottery.png)   \n ## Vậy PancakeSwap Caputure Value cho CAKE như thế nào?\n\nPancakeSwap đang tạo nên một cuộc cách mạng với mô hình Mint &amp; Burn kết hợp cùng veCAKE và hệ thống biểu quyết gauges, trao quyền cho người sở hữu CAKE để định hình tương lai của các liquidity pool. Bằng cách bỏ phiếu, veCAKE Holder có thể phân bổ CAKE Emission, ưu tiên các pool hoặc dự án yêu thích, mở ra cơ hội tối ưu hóa phần thưởng. Với veCAKE, bạn không chỉ là người tham gia mà còn là người dẫn dắt hệ sinh thái!\n\nveCAKE\n\n Holders có thể:\n\n- **Điều khiển Emission\n\n**: Trực tiếp quyết định cách phân bổ CAKE cho từng pool thanh khoản, dựa trên quyền biểu quyết tỷ lệ với số dư veCAKE. Quyền lực của bạn càng lớn, tác động càng sâu!\n\n\n- **Hợp tác với giao thức bên thứ ba\n\n**: Ủy quyền veCAKE cho các Liquid Wrappers hoặc thị trường Bribe để tự động hóa biểu quyết, nhận phần thưởng hấp dẫn hơn.\n\n\n- **Chinh phục hệ sinh thái PancakeSwap\n\n**: Power từ veCAKE (số lượng CAKE * thời gian lock) sẽ là thông số cho iCAKE (dùng cho IFO), bCAKE (dùng cho boosting yields farming).\n\n\nCơ chế Mint &amp; Burn – Tăng giá trị bền vững: Ngoài việc phân phối phần thưởng qua các sản phẩm, PancakeSwap đốt CAKE từ nhiều nguồn để giảm nguồn cung, đẩy giá trị lâu dài:\n\n- 0.001-0.23% phí giao dịch trên Exchange V3 (trừ Aptos).\n\n\n- 0.0575% phí giao dịch trên Exchange V2.\n\n\n- 0.004-0.02% phí từ StableSwap.\n\n\n- 20% lợi nhuận từ Perpetual Trading.\n\n\n- 100% phí hiệu suất CAKE từ IFO.\n\n\n- 100% CAKE dùng cho Profile Creation và NFT minting.\n\n\n- 100% CAKE từ người thắng Farm Auctions.\n\n\n- 2% doanh thu bán NFT trên NFT Market.\n\n\n- 20% CAKE từ \n\nviệc mua vé Lottery.\n\n\n- 3% mỗi \n\nround BNB/CAKE Prediction Markets\n\n dùng mua lại CAKE để burn.\n\n\n- 80% doanh thu từ bán tên miền .cake.\n\n\n![](https://statics.gemxresearch.com/images/2025/04/11/152944/tokenomic.png)  Đề xuất bỏ veTOKEN\n\nDù mô hình veCAKE ra mắt năm 2023 từng tạo dấu ấn với quyền biểu quyết mạnh mẽ, PancakeSwap nay đưa ra Đề xuất Tokenomics 3.0, quyết định gỡ bỏ hệ thống này để khắc phục những hạn chế cản bước hệ sinh thái.\n\nTrước hết, veCAKE tạo ra hệ thống quản trị phức tạp, yêu cầu khóa token dài hạn, khiến nhiều người dùng khó tiếp cận và làm giảm sự tham gia cộng đồng. Thứ hai, \n\ncơ chế gauges phân bổ phần thưởng thiếu hiệu quả\n\n, khi các pool thanh khoản nhỏ nhận tới 40% CAKE Emission nhưng chỉ đóng góp dưới 2% vào doanh thu, gây lãng phí tài nguyên.\n\nBên cạnh đó, việc khóa CAKE dài hạn làm mất tính linh hoạt, hạn chế quyền tự do sở hữu tài sản. Cuối cùng, sự thiếu đồng bộ giữa Emission và giá trị kinh tế từ các pool tạo ra mất cân bằng, ảnh hưởng đến lợi ích chung.\n\nVới Tokenomics 3.0, PancakeSwap mở ra một kỷ nguyên mới, tập trung vào bốn mục tiêu lớn lao:\n\n- Tăng quyền sở hữu thực sự: Xóa bỏ staking CAKE, veCAKE, gauges và chia sẻ doanh thu, trao trả tự do sử dụng token cho người dùng mà không cần khóa dài hạn.\n\n\n- Đơn giản hóa quản trị: Thay thế mô hình veCAKE rườm rà bằng hệ thống linh hoạt, chỉ cần stake CAKE trong thời gian biểu quyết, mở cửa cho mọi người tham gia dễ dàng.\n\n\n- Tăng trưởng bền vững: \n\nĐặt mục tiêu giảm phát 4%/năm\n\n, giảm 20% nguồn cung CAKE đến 2030. Lượng Emission CAKE hàng ngày giảm từ 40,000 xuống 22,500 qua ba giai đoạn, được đội ngũ quản lý dựa trên dữ liệu thị trường thời gian thực, ưu tiên pool thanh khoản lớn để tăng hiệu quả 30-40%. \n\nToàn bộ phí giao dịch chuyển sang đốt CAKE, nâng tỷ lệ đốt ở một số pool từ 10% lên 15\n\n%.\n\n\n- Hỗ trợ cộng đồng: Mở khóa toàn bộ CAKE đã stake và veCAKE mà không phạt, với thời hạn rút 6 tháng qua giao diện PancakeSwap. Người dùng veCAKE từ bên thứ ba (như CakePie, StakeDAO) sẽ chờ đối tác triển khai rút.\n\n\n \n ## Onchain Insights\n\n \n ### Các sản phẩm\n\nChúng ta đã nắm rõ cách CAKE tạo giá trị thông qua veTOKEN và cơ chế Mint &amp; Burn trong hệ sinh thái PancakeSwap. Xét về sản phẩm Lottery, doanh thu từ bán vé (Ticket Sale) trong 90 ngày từ 03/01 đến 14/04/2024 cho thấy xu hướng tăng trưởng không ổn định, với những giai đoạn tăng giảm rõ rệt. Cụ thể, Lottery ghi nhận các đợt tăng trưởng mạnh như 200% vào đầu tháng 1, 100% vào đầu tháng 2 và giữa tháng 3, nhưng cũng đối mặt với những đợt sụt giảm đáng kể từ 33% đến 50%, đặc biệt giảm mạnh vào cuối tháng 3 và đầu tháng 4. Dù có phục hồi nhẹ 50% vào ngày 14/4, mức tăng này không đủ để bù đắp cho sự sụt giảm trước đó, cho thấy Lottery chưa tạo được sức hút bền vững.\n\nĐối với sản phẩm Prediction, phí giao dịch trên BNB Chain (tính bằng USD) từ ngày 01/01/2024 đến 08/04/2024 cho thấy xu hướng tăng trưởng mạnh mẽ ban đầu, sau đó giảm dần nhưng vẫn duy trì ở mức cao hơn so với đầu kỳ. Cụ thể, phí giao dịch tăng đột biến từ 15K USD vào ngày 01/01 lên mức đỉnh 157.9K USD vào ngày 24/01, tương ứng với mức tăng trưởng ấn tượng 952.67%. Tuy nhiên, sau khi đạt đỉnh, phí bắt đầu giảm dần, dao động từ 149.4K USD (ngày 07/02) xuống 117K USD (ngày 07/03), rồi phục hồi nhẹ lên 123.6K USD (ngày 14/03), trước khi tiếp tục giảm còn 91.1K USD vào ngày 08/04. Từ mức đỉnh đến cuối kỳ, phí giảm 42.30%, tương đương 66.8K USD. Dù vậy, so với đầu kỳ, phí giao dịch vẫn tăng trưởng mạnh 507.33%, từ 15K USD lên 91.1K USD.\n\nTại Perp, từ năm 2023 đến nay, mức phí thu được đạt đỉnh vào cuối quý 1/2024 với tổng cộng $330,673, ghi nhận mức tăng trưởng ấn tượng 1059.6% so với tháng 4/2023. Tuy nhiên, từ quý 2/2024, nguồn phí này bắt đầu suy giảm và kéo dài đến thời điểm hiện tại. So với mức phí cao nhất mọi thời đại (ATH) vào ngày 08/03/2024, con số này đã giảm mạnh xuống còn $20,451, tương ứng với mức giảm 93.8%. Về đóng góp, phần lớn phí đến từ BSC và ARB, trong khi OPBNB và Base chỉ chiếm một phần rất nhỏ, gần như không đáng kể trong tổng thể.\n\n \n ### Token\n\nVề lượng CAKE, hơn 93% được khóa để nhận veCAKE, trong khi 6.7% còn lại được phân bổ vào các Pool khác nhau (CAKE Pool). Từ tháng 1/2024 đến nay, xu hướng Net Mint của CAKE chủ yếu âm, cho thấy nguồn cung đang giảm phát một cách tích cực. Điều này phản ánh các sản phẩm trong hệ sinh thái CAKE vẫn duy trì đủ nhu cầu để thúc đẩy lượng Burn hàng tuần.\n\nDù PancakeSwap sở hữu nhiều sản phẩm đa dạng ngoài AMM và tích hợp chúng vào cơ chế Mint &amp; Burn, phần lớn lượng Burn lại đến từ hoạt động trên AMM Dex, trong khi các sản phẩm khác chỉ đóng góp khoảng 11.1% vào quá trình Burn. Điều này cho thấy AMM vẫn là động lực chính trong việc duy trì cơ chế giảm phát của CAKE.\n\n \n ## Tổng kết\n\nMô hình của Pancake nổi bật với sự đa dạng vượt trội so với các sàn DEX khác, không chỉ dừng lại ở DEX mà còn tích hợp nhiều sản phẩm nhằm thúc đẩy cơ chế Burn, tạo sự cân bằng với lượng Emission để thu hút thanh khoản. Điểm nhấn là cơ chế veTOKEN, về lý thuyết, giúp khóa nguồn cung, giảm áp lực bán tháo lên biểu đồ giá. Tuy nhiên, thực tế lại cho thấy veTOKEN gây ra không ít trở ngại trong việc điều phối Emission, dẫn đến hạn chế cho các Liquidity Pools có TVL thấp, làm dấy lên những thách thức trong vận hành.\n\nDù Pancake hướng đến xây dựng một hệ sinh thái linh hoạt, bền vững, ưu tiên lợi ích cộng đồng và hiệu quả dài hạn, nhưng các đề xuất gần đây lại vấp phải tranh cãi xoay quanh tính phi tập trung và niềm tin từ cộng đồng. Những cuộc tranh luận này phản ánh sự cạnh tranh khốc liệt và cả những \"trò chơi chính trị\" trong nội bộ hệ sinh thái.\n\nMột vấn đề đáng chú ý là sự xuất hiện của các Liquid Wrappers – một hiện tượng phổ biến trong các dự án áp dụng mô hình veTOKEN, nhằm chiếm quyền sở hữu lượng lớn veTOKEN. Tuy nhiên, Pancake bị nghi ngờ đã âm thầm tích lũy CAKE để nâng tỷ lệ sở hữu veTOKEN lên gần 50%, vượt mặt các Liquid Wrappers. Đỉnh điểm là đề xuất loại bỏ hoàn toàn veTOKEN, gây ra nhiều tranh cãi.\n\n [Twitter Post](https://twitter.com/defiwars_/status/1909955376147059114)Nếu đề xuất này được thông qua, các Liquid Wrappers phụ thuộc vào veTOKEN sẽ đối mặt với nguy cơ sụp đổ hoàn toàn, do bản chất tồn tại của chúng dựa vào lượng veTOKEN nắm giữ. Mặt khác, việc loại bỏ veTOKEN có thể mang lại lợi ích lớn hơn cho Pancake, củng cố mô hình Mint &amp; Burn và gia tăng giá trị cho CAKE. Tuy nhiên, động thái này không chỉ là một quyết định chiến lược mà còn là một bước đi đầy rủi ro, có thể định hình lại niềm tin và tương lai của hệ sinh thái Pancake.\n\n&nbsp;\n\n**Tất cả chỉ vì mục đích thông tin tham khảo, bài viết này hoàn toàn không phải là lời khuyên đầu tư\n\n     ** &nbsp;\n\nHy vọng với những thông tin trên sẽ giúp các bạn có nhiều insights thông qua \n\nCapWheel Series Pancake Swap\n\n. Những thông tin về dự án mới nhất sẽ luôn được cập nhật nhanh chóng trên website và các kênh chính thức của \n\nGFI Research\n\n. Các bạn quan tâm đừng quên tham gia vào nhóm cộng đồng của GFI để cùng thảo luận, trao đổi kiến thức và kinh nghiệm với các thành viên khác nhé.\n\n     &nbsp;\n\n&nbsp;\n\n\n\n\n    ~~~metadata \n\n    undefined: undefined\nundefined: undefined\nundefined: undefined\nExcerpt: Pancake nổi bật so với các sàn DEX khác nhờ hệ sinh thái đa dạng, tích hợp nhiều sản phẩm nhằm thúc đẩy cơ chế Burn trong mô hình Mint & Burn của CAKE. Tuy nhiên, phần lớn lượng CAKE được Burn vẫn đến từ các hoạt động DEX, trong khi các sản phẩm khác chỉ đóng góp khoảng 11% vào tổng lượng Burn.\n\nĐề xuất loại bỏ veCAKE được đưa ra với mục tiêu kiểm soát nguồn cung hiệu quả hơn, nhưng lại vấp phải tranh cãi gay gắt về tính phi tập trung. Pancake bị nghi ngờ đã có những động thái không minh bạch nhằm giảm sức ép từ các Liquid Wrappers trước khi đề xuất được đưa vào biểu quyết, làm dấy lên nhiều lo ngại trong cộng đồng.\nundefined: undefined\nundefined: undefined\nMeta description: Pancake nổi bật so với các sàn DEX khác nhờ hệ sinh thái đa dạng, tích hợp nhiều sản phẩm nhằm thúc đẩy cơ chế Burn trong mô hình Mint & Burn.\n postUrl: capwheel-series-pancakeswap \n ~~~"

    import time

    start = time.time()

    llm = AzureChatOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        model="o3-mini",
        api_version="2024-12-01-preview",
    )

    print(check_fact(llm,text,os.getenv("SEARXNG_URL")))

    end = time.time()
    print(f"Time taken: {end - start} seconds")