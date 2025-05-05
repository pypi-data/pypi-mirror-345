"""
This module provides comprehensive evaluation functionality for crypto/Web3 research articles 
following GFI Research style guidelines. It analyzes article structure, content quality,
grammar/language usage, and SEO optimization.

Key features:
- Article structure validation
- Content quality assessment 
- Grammar and style checking
- SEO optimization analysis
- Comprehensive evaluation reporting
"""

from langchain_openai import AzureChatOpenAI

def check_content(llm: AzureChatOpenAI, text: str) -> str:
    
    prompt = f"""
<system>
    You are a content analysis expert with extensive experience in evaluating the quality and information value of research articles. Your task is to thoroughly assess content according to specific criteria, providing scores and detailed, objective feedback. Your evaluation must be evidence-based, professional, fair, and helpful.
</system>

<prompt>
    <task>
        <description>Evaluate the provided content based on quality criteria and provide detailed feedback</description>
        <content_to_evaluate>
            {text}
        </content_to_evaluate>
    </task>
    
    <evaluation_criteria>
        <criterion id="practical_value">
        <name>Practical Value</name>
        <description>Content must be practical and deliver tangible value to readers</description>
        <questions>
            <question>Does the content provide useful and applicable information?</question>
            <question>Do readers gain specific and practical benefits?</question>
            <question>Are there actionable guidelines or suggestions for readers to implement?</question>
        </questions>
        <scoring>Score this criterion on a scale of 0-100, where 0 is completely impractical and 100 is exceptionally practical and valuable</scoring>
        </criterion>
        
        <criterion id="research_quality">
        <name>Research Quality</name>
        <description>Content should provide analysis, interpretation, and arguments based on independent and in-depth research</description>
        <questions>
            <question>Is the analysis based on independent and in-depth research?</question>
            <question>Are the arguments and conclusions logical and convincing?</question>
            <question>Is there clear evidence supporting the analyses?</question>
        </questions>
        <scoring>Score this criterion on a scale of 0-100, where 0 is completely lacking research and 100 is exceptional research quality</scoring>
        </criterion>
        
        <criterion id="depth_breadth">
        <name>Depth and Breadth</name>
        <description>Provides comprehensive information about the research topic</description>
        <questions>
            <question>Does the content delve deeply into the subject rather than just introducing the surface?</question>
            <question>Does it provide specialized knowledge and important details?</question>
            <question>Is the topic explored from multiple angles and aspects?</question>
        </questions>
        <scoring>Score this criterion on a scale of 0-100, where 0 is extremely superficial and 100 is exceptionally deep and comprehensive</scoring>
        </criterion>
        
        <criterion id="comprehensiveness">
        <name>Comprehensiveness and Reader Priority</name>
        <description>Maximizes exploration of multiple aspects of the issue and prioritizes reader benefits</description>
        <questions>
            <question>Does the content address questions or issues that readers care about?</question>
            <question>Does it consider all dimensions of the issue?</question>
            <question>Is the information presented focused on reader benefits?</question>
        </questions>
        <scoring>Score this criterion on a scale of 0-100, where 0 is extremely narrow in scope and 100 is fully comprehensive and reader-focused</scoring>
        </criterion>
        
        <criterion id="data_credibility">
        <name>Data Credibility</name>
        <description>Data and information sources must be reliable and verifiable</description>
        <questions>
            <question>Are data sources clearly cited and from reliable sources?</question>
            <question>Is the data up-to-date and reflecting the latest information?</question>
            <question>Is the information accurate and free from biased viewpoints?</question>
        </questions>
        <scoring>Score this criterion on a scale of 0-100, where 0 is completely unreliable and 100 is extremely credible and well-sourced</scoring>
        </criterion>
    </evaluation_criteria>
    
    <output_format>
        <format>Markdown</format>
        <instructions>
            <instruction>Format your evaluation as a well-structured markdown document</instruction>
            <instruction>Use headers, lists, bold text, and other markdown elements for clarity</instruction>
            <instruction>Include a summary section at the top with scores for each criterion (0-100) and overall score</instruction>
            <instruction>Provide detailed analysis below the summary</instruction>
            <instruction>If any issues are identified, clearly specify the exact location in the content and explain in detail why it's problematic</instruction>
        </instructions>
        <note>Return results as lists only, not as tables or any other format. Provide exactly what is requested without additional symbols or explanations.</note>
    </output_format>
    
    <instructions>
        <instruction>Read the entire content carefully</instruction>
        <instruction>Evaluate each criterion objectively and assign a score from 0-100</instruction>
        <instruction>Provide specific reasons for each score</instruction>
        <instruction>Calculate the overall score as a weighted average of all criteria</instruction>
        <instruction>Pay special attention to practical value and information reliability</instruction>
        <instruction>For any problematic content, quote the specific text and explain why it doesn't meet the criteria</instruction>
        <instruction>Return the evaluation as a professionally formatted markdown document</instruction>
        <instruction>Include specific page/paragraph references when identifying issues</instruction>
    </instructions>
</prompt>
"""
    response = llm.invoke(prompt)

    return response.content

def check_methodology_objectivity(llm: AzureChatOpenAI, text: str) -> str:
    prompt = f"""
<system>
    You are an expert analyst specializing in evaluating research in Web3, DeFi, and cryptocurrency markets. Your task is to assess the research methodology and objectivity of analytical articles according to specific criteria, providing scores and detailed feedback. Your evaluation must be evidence-based, professional, fair, and helpful.
</system>
<prompt>
    <task>
        <description>Evaluate the research methodology and objectivity of the provided content based on specific criteria and provide detailed feedback</description>
        <content_to_evaluate>
            {text}
        </content_to_evaluate>
    </task>
<evaluation_criteria>
    <criterion id="multiple_sources">
    <name>Diverse Source Material</name>
    <description>Content should compare information from multiple different sources</description>
    <questions>
        <question>Does the article cite and utilize data from diverse sources (both official project sources and third parties)?</question>
        <question>Is there cross-referencing and comparison between different data sources?</question>
        <question>Are the sources reliable and reputable within the Web3/DeFi space?</question>
        <question>Does the author use on-chain data and analytical tools like Dune Analytics, TradingView for illustration?</question>
    </questions>
    <scoring>Score this criterion on a scale of 0-100, where 0 is completely lacking source diversity and 100 is excellent with multiple reliable sources</scoring>
    </criterion>
    
    <criterion id="research_based_evaluation">
    <name>Research-Based Assessment</name>
    <description>Provides results/comments/evaluations based on research findings</description>
    <questions>
        <question>Are the assessments and conclusions based on specific data and factual analysis?</question>
        <question>Does the article deeply analyze core technology, roadmap, and growth potential of the project?</question>
        <question>Are tokenomics and valuation judgments based on substantiated analytical models and methods?</question>
        <question>Are investment strategies proposed with data-backed reasoning?</question>
    </questions>
    <scoring>Score this criterion on a scale of 0-100, where 0 is completely lacking research-based analysis and 100 is excellent analysis with well-founded assessments</scoring>
    </criterion>
    
    <criterion id="multidimensional_view">
    <name>Multidimensional Perspective</name>
    <description>Article provides a multifaceted view of the research subject</description>
    <questions>
        <question>Does the author present both strengths and weaknesses of the analyzed project/trend?</question>
        <question>Does the article consider risk factors and potential challenges?</question>
        <question>Is there comparison with competing projects in the same segment?</question>
        <question>Does the author express personal viewpoints while remaining objective about alternative perspectives?</question>
    </questions>
    <scoring>Score this criterion on a scale of 0-100, where 0 is completely lacking multidimensional perspective and 100 is extremely balanced and comprehensive</scoring>
    </criterion>
    
    <criterion id="scope_appropriateness">
    <name>Appropriate Research Scope</name>
    <description>Topic is executed within a scope that is neither too broad nor too narrow</description>
    <questions>
        <question>Is the research scope specific enough to delve into important issues?</question>
        <question>Does the article focus on the most essential aspects of the project/topic?</question>
        <question>Is there a balance between technical analysis and market/investment analysis?</question>
        <question>Is the content appropriate for the target audience of individual investors?</question>
    </questions>
    <scoring>Score this criterion on a scale of 0-100, where 0 is completely inappropriate scope and 100 is ideal research scope</scoring>
    </criterion>
    
    <criterion id="crypto_specific_quality">
    <name>Crypto-Specific Quality</name>
    <description>Evaluates the quality of analysis for crypto-specific factors</description>
    <questions>
        <question>Does the article provide detailed analysis of tokenomics, unlock schedules, and market capitalization?</question>
        <question>Is there analysis of on-chain data and user behavior metrics?</question>
        <question>Does the author update and analyze the impact of events and regulations from Fed, SEC?</question>
        <question>Are macroeconomic factors affecting the crypto market addressed?</question>
    </questions>
    <scoring>Score this criterion on a scale of 0-100, where 0 is completely lacking crypto-specific understanding and 100 is deep understanding of crypto markets</scoring>
    </criterion>
</evaluation_criteria>

<output_format>
    <format>Markdown</format>
    <instructions>
        <instruction>Format your evaluation as a well-structured markdown document</instruction>
        <instruction>Use headers, lists, bold text, and other markdown elements for clarity</instruction>
        <instruction>Include a summary section at the top with scores for each criterion (0-100) and overall score</instruction>
        <instruction>Provide detailed analysis below the summary</instruction>
        <instruction>If any issues are identified, clearly specify the exact location in the content and explain in detail why it's problematic</instruction>
    </instructions>
    <note>Return results as lists only, not as tables or any other format. Provide exactly what is requested without additional symbols or explanations.</note>
</output_format>

<instructions>
    <instruction>Read the entire content carefully</instruction>
    <instruction>Evaluate each criterion objectively and assign a score from 0-100</instruction>
    <instruction>Provide specific reasons for each score</instruction>
    <instruction>Calculate the overall score as a weighted average of all criteria</instruction>
    <instruction>Pay special attention to the use of multiple data sources and objectivity in assessment</instruction>
    <instruction>For any problematic content, quote the specific text and explain why it doesn't meet the criteria</instruction>
    <instruction>Return the evaluation as a professionally formatted markdown document</instruction>
    <instruction>Include specific page/paragraph references when identifying issues</instruction>
</instructions>
</prompt>
"""
    
    response = llm.invoke(prompt)

    return response.content

def check_format_presentation(llm: AzureChatOpenAI, text: str) -> str:
    prompt = f"""
<system>
    You are an expert content evaluator specializing in Web3, DeFi, and cryptocurrency market research presentations. Your task is to assess the form, structure, and presentation quality of analytical articles according to specific criteria, providing scores and detailed feedback. Your evaluation must be evidence-based, professional, fair, and helpful.
</system>
<prompt>
    <task>
        <description>Evaluate the form and presentation of the provided content based on specific criteria and provide detailed feedback</description>
        <content_to_evaluate>
            {text}
        </content_to_evaluate>
    </task>
    <evaluation_criteria>
        <criterion id="writing_style">
            <name>Clear and Objective Writing Style</name>
            <description>Content should be written in a clear, objective manner appropriate for research analysis</description>
            <questions>
                <question>Is the writing style clear, precise, and easy to understand?</question>
                <question>Does the author maintain objectivity throughout the analysis?</question>
                <question>Is the tone professional while remaining accessible to individual investors?</question>
                <question>Are technical concepts explained clearly without unnecessary jargon?</question>
            </questions>
            <scoring>Score this criterion on a scale of 0-100, where 0 is completely unclear/biased and 100 is exceptionally clear and objective</scoring>
        </criterion>

        <criterion id="structure_organization">
            <name>Clear Structure and Logical Organization</name>
            <description>Content should have a clear structure with logical arrangement and coherence between sections</description>
            <questions>
                <question>Is the content organized with a logical flow from introduction to conclusion?</question>
                <question>Are there clear transitions between different sections and topics?</question>
                <question>Does the structure help the reader follow the analysis easily?</question>
                <question>Is there appropriate use of subheadings to guide the reader through the content?</question>
            </questions>
            <scoring>Score this criterion on a scale of 0-100, where 0 is completely disorganized and 100 is perfectly structured</scoring>
        </criterion>

        <criterion id="heading_hierarchy">
            <name>Proper Heading Hierarchy</name>
            <description>Content uses correct heading levels with H1 only for the main title and H2+ for content sections</description>
            <questions>
                <question>Is H1 used only for the main title of the article?</question>
                <question>Are content sections properly organized with H2 headings and subsequent subheadings?</question>
                <question>Is there a consistent heading hierarchy throughout the document?</question>
                <question>Do headings effectively summarize the content that follows them?</question>
            </questions>
            <scoring>Score this criterion on a scale of 0-100, where 0 is completely incorrect heading usage and 100 is perfect heading hierarchy</scoring>
        </criterion>

        <criterion id="grammar_spelling">
            <name>Grammar and Spelling Accuracy</name>
            <description>Content should be free of grammatical errors and spelling mistakes</description>
            <questions>
                <question>Is the content free from spelling errors?</question>
                <question>Is the grammar correct throughout the document?</question>
                <question>Are punctuation marks used appropriately?</question>
                <question>Is the vocabulary appropriate for the target audience?</question>
            </questions>
            <scoring>Score this criterion on a scale of 0-100, where 0 is filled with errors and 100 is error-free</scoring>
        </criterion>

        <criterion id="visual_presentation">
            <name>Visual Presentation Quality</name>
            <description>Content includes effective use of charts, graphs, and formatting to enhance understanding</description>
            <questions>
                <question>Are charts and graphs used effectively to illustrate key points?</question>
                <question>Is formatting (bold, italics, lists, etc.) used appropriately to highlight important information?</question>
                <question>Do visual elements have clear captions and explanations?</question>
                <question>Is there a balanced use of text and visual elements?</question>
            </questions>
            <scoring>Score this criterion on a scale of 0-100, where 0 is poor visual presentation and 100 is excellent visual presentation</scoring>
        </criterion>
    </evaluation_criteria>

    <output_format>
        <format>Markdown</format>
        <instructions>
            <instruction>Format your evaluation as a well-structured markdown document</instruction>
            <instruction>Use headers, lists, bold text, and other markdown elements for clarity</instruction>
            <instruction>Include a summary section at the top with scores for each criterion (0-100) and overall score</instruction>
            <instruction>Provide detailed analysis below the summary</instruction>
            <instruction>If any issues are identified, clearly specify the exact location in the content and explain in detail why it's problematic</instruction>
        </instructions>
        <note>Return results as lists only, not as tables or any other format. Provide exactly what is requested without additional symbols or explanations.</note>
    </output_format>

    <instructions>
        <instruction>Read the entire content carefully</instruction>
        <instruction>Evaluate each criterion objectively and assign a score from 0-100</instruction>
        <instruction>Provide specific reasons for each score</instruction>
        <instruction>Calculate the overall score as a weighted average of all criteria</instruction>
        <instruction>Pay special attention to heading hierarchy and writing style clarity</instruction>
        <instruction>For any problematic content, quote the specific text and explain why it doesn't meet the criteria</instruction>
        <instruction>Return the evaluation as a professionally formatted markdown document</instruction>
        <instruction>Include specific page/paragraph/section references when identifying issues</instruction>
    </instructions>
</prompt>
"""
    
    response = llm.invoke(prompt)

    return response.content

def check_professional_technical(llm: AzureChatOpenAI, text: str) -> str:
    prompt = f"""
<system>
    You are an expert technical evaluator specializing in Web3, DeFi, and cryptocurrency market research publications.
    Your task is to assess the technical professionalism of analytical articles according to specific criteria,
    with special focus on citation practices and link formatting. Your evaluation must be evidence-based, professional, fair, and helpful.
</system>
<prompt>
    <task>
        <description>Evaluate the technical professionalism of the provided content based on specific criteria and provide detailed feedback</description>
        <content_to_evaluate>
            {text}
        </content_to_evaluate>
    </task>
    <evaluation_criteria>
        <criterion id="citation_credibility">
            <name>Citation Credibility and Authority</name>
            <description>Referenced links and citations must come from reputable sources</description>
            <questions>
                <question>Do the cited sources come from reputable organizations, projects, or industry experts?</question>
                <question>Are official project documentation, whitepapers, and primary sources utilized?</question>
                <question>Are data references linked to established analytics platforms like Dune Analytics, Glassnode, or CoinMarketCap?</question>
                <question>Do the sources represent diverse viewpoints and not just those that support the author's thesis?</question>
            </questions>
            <scoring>Score this criterion on a scale of 0-100, where 0 indicates completely unreliable sources and 100 indicates perfectly credible sources</scoring>
        </criterion>

        <criterion id="internal_linking">
            <name>Internal Link Formatting</name>
            <description>Internal links should use relative paths rather than absolute URLs</description>
            <questions>
                <question>Are internal links formatted using relative paths (e.g., /tong-quan-ve-du-an-bit-country.html)?</question>
                <question>Are absolute URLs avoided for internal resources?</question>
                <question>Are internal links descriptive and relevant to the content they point to?</question>
                <question>Do internal links enhance the reader's ability to navigate related content?</question>
            </questions>
            <scoring>Score this criterion on a scale of 0-100, where 0 indicates completely incorrect internal linking and 100 indicates perfect implementation</scoring>
        </criterion>

        <criterion id="email_linking">
            <name>Email Link Formatting</name>
            <description>Email links should use the mailto: protocol format</description>
            <questions>
                <question>Are email links properly formatted using the mailto: protocol (e.g., mailto:abc@gmail.com)?</question>
                <question>Are plain text email addresses avoided as clickable links?</question>
                <question>Are email links used appropriately and only when necessary?</question>
                <question>Do email links function properly when tested?</question>
            </questions>
            <scoring>Score this criterion on a scale of 0-100, where 0 indicates completely incorrect email formatting and 100 indicates perfect implementation</scoring>
        </criterion>

        <criterion id="general_link_quality">
            <name>General Link Quality and Functionality</name>
            <description>Overall assessment of link quality, relevance, and technical implementation</description>
            <questions>
                <question>Are links descriptive and avoid generic text like "click here"?</question>
                <question>Do links open in appropriate windows/tabs based on context?</question>
                <question>Are links up-to-date and not leading to deprecated content?</question>
                <question>Is there an appropriate density of links (not too few or too many)?</question>
            </questions>
            <scoring>Score this criterion on a scale of 0-100, where 0 indicates poor overall link quality and 100 indicates excellent implementation</scoring>
        </criterion>

        <criterion id="technical_accuracy">
            <name>Technical Information Accuracy</name>
            <description>Assessment of the accuracy of technical descriptions and explanations</description>
            <questions>
                <question>Are technical concepts explained accurately and with appropriate detail?</question>
                <question>Are protocol specifications, tokenomics, and technical architectures correctly described?</question>
                <question>Is there consistency in technical terminology throughout the document?</question>
                <question>Are technical claims supported by verifiable references?</question>
            </questions>
            <scoring>Score this criterion on a scale of 0-100, where 0 indicates completely inaccurate technical information and 100 indicates perfect technical accuracy</scoring>
        </criterion>
    </evaluation_criteria>

    <output_format>
        <format>Markdown</format>
        <instructions>
            <instruction>Format your evaluation as a well-structured markdown document</instruction>
            <instruction>Use headers, lists, bold text, and other markdown elements for clarity</instruction>
            <instruction>Include a summary section at the top with scores for each criterion (0-100) and overall score</instruction>
            <instruction>Provide detailed analysis below the summary</instruction>
            <instruction>If any issues are identified, clearly specify the exact location in the content and explain in detail why it's problematic</instruction>
        </instructions>
        <note>Return results as lists only, not as tables or any other format. Provide exactly what is requested without additional symbols or explanations.</note>
    </output_format>

    <instructions>
        <instruction>Read the entire content carefully</instruction>
        <instruction>Evaluate each criterion objectively and assign a score from 0-100</instruction>
        <instruction>Provide specific reasons for each score</instruction>
        <instruction>Calculate the overall score as a weighted average of all criteria</instruction>
        <instruction>Pay special attention to citation credibility and proper link formatting</instruction>
        <instruction>For any problematic content, quote the specific text and explain why it doesn't meet the criteria</instruction>
        <instruction>Return the evaluation as a professionally formatted markdown document</instruction>
        <instruction>Include specific examples of both correct and incorrect implementations found in the content</instruction>
    </instructions>
</prompt>
"""

    response = llm.invoke(prompt)

    return response.content

def check_seo(llm: AzureChatOpenAI, text: str, metadata: str = None, keywords: str = "No keywords") -> str:
    """
    Performs comprehensive SEO evaluation for crypto research articles.
    
    Args:
        llm: AzureChatOpenAI instance for SEO analysis
        text: Article content to evaluate
        metadata: Optional metadata about the article
        
    Returns:
        str: Detailed SEO optimization report
        
    Analyzes:
    - Keyword optimization
    - Link structure
    - URL optimization
    - Content structure
    - Technical SEO elements
    """
    prompt = f"""
<prompt>
    <instruction>
        <role>Bạn là chuyên gia SEO có nhiệm vụ kiểm tra nội dung trang web và đánh giá mức độ tối ưu hóa.</role>
        <task>Phân tích thông tin trang web bao gồm: nội dung markdown, metadata và danh sách keyword. Nếu chưa có keyword, hãy xác định tối đa 3 keyword chính từ nội dung. Đánh giá theo tiêu chí đã cho với ký hiệu ✅ (đạt) hoặc ❌ (chưa đạt), kèm giải thích cụ thể và chỉ rõ vị trí cần khắc phục. Ngoài ra, hãy gợi ý 5 URL thân thiện với SEO dựa trên nội dung bài viết.</task>
        <note>Chỉ trả về kết quả đánh giá theo yêu cầu, không thêm thông tin phụ. Định dạng kết quả bằng markdown.</note>
    </instruction>
  
    <criteria>
        <category name="Tối ưu từ khóa">
            <item id="kw1">Từ khóa xuất hiện trong Title SEO</item>
            <item id="kw2">Từ khóa xuất hiện trong Meta Description</item>
            <item id="kw3">Từ khóa xuất hiện trong H1, H2, H3</item>
            <item id="kw4">Từ khóa xuất hiện trong đoạn Sapo (đoạn mở đầu)</item>
            <item id="kw5">Từ khóa xuất hiện trong đoạn kết</item>
            <item id="kw6">Từ khóa phân bổ đều trong bài viết</item>
            <item id="kw7">Mật độ từ khóa đạt 1-5%</item>
            <item id="kw8">Mỗi đoạn chứa tối đa 2 từ khóa khác nhau</item>
        </category>
    
        <category name="Cấu trúc nội dung">
            <item id="st1">Có đoạn Sapo (đoạn mở đầu)</item>
            <item id="st2">Có Title & Meta SEO cho social</item>
            <item id="st3">Có thẻ H1</item>
            <item id="st4">Có thẻ H2, H3</item>
            <item id="st5">Có Title SEO và độ dài không quá 70 ký tự</item>
            <item id="st6">Có Meta description và độ dài không quá 160 ký tự</item>
        </category>
        
        <category name="Liên kết">
            <item id="lk1">Có Internal link</item>
            <item id="lk2">Có External link. Check các link external là link no hoặc dofollow, nếu link dofollow[DO] thì thông báo lại cụ thể từng link.(trước các link có ký hiệu [NO/DO])</item>
            <item id="lk3">Có link đến 3 bài viết liên quan</item>
            <item id="lk4">Đoạn sapo chỉ chèn link trang chủ hoặc không chèn link nào cả</item>
        </category>
        
        <category name="Chất lượng nội dung">
            <item id="ct1">Có thông tin năm/tháng cụ thể (nếu liên quan)</item>
            <item id="ct2">Có đoạn mở đầu hấp dẫn</item>
            <item id="ct3">Có đoạn kết tổng hợp</item>
            <item id="ct4">Nội dung độc đáo (không trùng lặp)</item>
            <item id="ct5">Câu văn ngắn gọn, mỗi đoạn tối đa 3 câu</item>
            <item id="ct6">Thể hiện quan điểm, cảm xúc, trải nghiệm cá nhân; đề cập đến bản thân/thương hiệu GFI để tăng uy tín</item>
        </category>
    </criteria>

    <output_format>
        <markdown>
            ## Kết quả đánh giá SEO
            
            ### Từ khóa đã phân tích
            - [keyword_list]
            
            ### Tối ưu từ khóa
            [keyword_optimization_results]
            
            ### Cấu trúc nội dung
            [structure_results]
            
            ### Liên kết
            [link_results]
            
            ### Chất lượng nội dung
            [content_quality_results]
            
            ## Báo cáo tổng hợp
            
            ### Điểm mạnh
            [strengths]
            
            ### Điểm cần cải thiện
            [weaknesses]
            
            ### Đề xuất cải thiện
            [recommendations]
            
            ### Phân tích từ khóa
            - **Từ khóa chính:** [main_keywords]
            - **Mật độ từ khóa:** [keyword_density]
            
            ### Gợi ý URL thân thiện với SEO
            1. https://gfiresearch.net/post/[url_suggestion_1]
            2. https://gfiresearch.net/post/[url_suggestion_2]
            3. https://gfiresearch.net/post/[url_suggestion_3]
            4. https://gfiresearch.net/post/[url_suggestion_4]
            5. https://gfiresearch.net/post/[url_suggestion_5]
        </markdown>
    </output_format>

    <url_suggestion_guidelines>
        <guideline>URL nên ngắn gọn, dễ đọc và chứa từ khóa chính</guideline>
        <guideline>Sử dụng dấu gạch ngang (-) thay vì gạch dưới (_) hoặc khoảng trắng</guideline>
        <guideline>Loại bỏ các từ không cần thiết như "a", "an", "the", "and", "or", "but"</guideline>
        <guideline>Tránh sử dụng ký tự đặc biệt, dấu câu và số nếu không cần thiết</guideline>
        <guideline>URL nên phản ánh nội dung chính của bài viết</guideline>
        <guideline>Nếu có từ khóa có dấu tiếng Việt, chuyển thành không dấu</guideline>
    </url_suggestion_guidelines>

    <content>
        {text}
    </content>

    <metadata>
        {metadata}
    </metadata>

    <keywords>
        {keywords}
    </keywords>
</prompt>
"""

    # Invoke the LLM with the comprehensive evaluation prompt
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error during evaluation: {str(e)}"


    pass

def check_text(llm: AzureChatOpenAI, text: str) -> str:
    """
    Master function that performs comprehensive article evaluation by combining
    all individual analysis components.
    
    Args:
        llm: AzureChatOpenAI instance for text analysis
        text: Article content to evaluate
        
    Returns:
        str: Complete evaluation report including:
        - Executive summary
        - Structure analysis
        - Content quality assessment 
        - Language evaluation
        - SEO optimization report
        - Improvement recommendations
        
    The function coordinates multiple specialized evaluations and combines
    their results into a single, well-organized report in Vietnamese.
    """
    # Collect all individual evaluation results asynchronously if possible
    # If async not available, we'll call them sequentially

    # Add input validation
    if not text or not isinstance(text, str):
        return "Invalid input: Text must be a non-empty string"
    if not llm:
        return "Invalid input: Language model required"

    blog = text.split("~~~metadata")
    text = blog[0]
    metadata = blog[1][:-3]

    try:
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        async def run_evaluations():
            with ThreadPoolExecutor(max_workers=5) as executor:
                seo_task = executor.submit(check_seo, llm, text, metadata)
                content_task = executor.submit(check_content, llm, text)
                methodology_objectivity_task = executor.submit(check_methodology_objectivity, llm, text)
                format_presentation = executor.submit(check_format_presentation, llm, text)
                professional_technical = executor.submit(check_professional_technical, llm, text)
                
                # Wait for all tasks to complete
                # This is more efficient than sequential execution
                check_seo_result = seo_task.result()
                check_content_result = content_task.result()
                check_methodology_objectivity_result = methodology_objectivity_task.result()
                check_format_presentation_result = format_presentation.result()
                check_professional_technical_result = professional_technical.result()
                
                
                return check_seo_result, check_content_result, check_methodology_objectivity_result, check_format_presentation_result, check_professional_technical_result
        
        # Run evaluations concurrently
        check_seo_result, check_content_result, check_methodology_objectivity_result, check_format_presentation_result, check_professional_technical_result = asyncio.run(run_evaluations())
        
    except (ImportError, RuntimeError):
        # Fallback to sequential execution if async is not available
        check_seo_result = check_seo(llm, text, metadata)
        check_content_result = check_content(llm, text)
        check_methodology_objectivity_result = check_methodology_objectivity(llm, text)
        check_format_presentation_result = check_format_presentation(llm, text)
        check_professional_technical_result = check_professional_technical(llm, text)

    # Combine all results into a structured format
    combined_result = f"""
# Kết quả đánh giá nội dung và giá trị thông tin:
{check_content_result}

# Kết quả đánh giá phương pháp nghiên cứu và tính khách quan:
{check_methodology_objectivity_result}

# Kết quả đánh giá hình thức và trình bày:
{check_format_presentation_result}

# Kết quả đánh giá tính chuyên nghiệp và kỹ thuật:
{check_professional_technical_result}

# Kết quả đánh giá SEO:
{check_seo_result}
    """
    
    # Format the detailed report with proper Markdown and translate to Vietnamese
    formatting_prompt = """
    <FormattingRequest>
        <Role>
            You are an expert editor specializing in technical documentation and SEO analysis.
        </Role>
        
        <Task>
            Format the following evaluation results into a well-structured and visually appealing Markdown document.
            Translate all content into Vietnamese while preserving technical terms.
            The output should be clean, professional, and easy to navigate.
        </Task>
        
        <Guidelines>
            <Guideline>Use clear hierarchy with headings (#, ##, ###) and subheadings</Guideline>
            <Guideline>Transform lists into properly formatted bullet points or numbered lists</Guideline>
            <Guideline>Use tables where appropriate for comparative data</Guideline>
            <Guideline>Use bold and italic formatting to highlight important information</Guideline>
            <Guideline>Preserve all technical terms, scores, and metrics</Guideline>
            <Guideline>Maintain a consistent style throughout the document</Guideline>
            <Guideline>Return only the formatted markdown without code blocks or explanations</Guideline>
        </Guidelines>
        
        <Content>
        {result}
        </Content>
    </FormattingRequest>
    """
    
    detailed_result = llm.invoke(formatting_prompt.format(result=combined_result)).content
    
    # Create summary with scores and key points
    summary_prompt = """
<system>
    You are an expert content strategist specializing in Web3, DeFi, and cryptocurrency market research publications. Your task is to create a comprehensive executive summary of multiple evaluation results, providing an overall score and actionable insights. Your summary must be evidence-based, professional, fair, and helpful.
</system>

<prompt>
    <task>
        <description>Create a concise executive summary of the evaluation results with an overall score and actionable insights</description>
        <content_to_evaluate>
            {result}
        </content_to_evaluate>
    </task>

    <output_requirements>
        <section id="overall_score">
            <name>Overall Score</name>
            <description>Calculate an overall weighted score on a scale of 0-100 based on all evaluation sections</description>
            <instructions>
                <instruction>Calculate the average score across all five evaluation sections</instruction>
                <instruction>Round the final score to one decimal place</instruction>
                <instruction>Provide a brief qualitative assessment of the overall score (Excellent: 90-100, Good: 75-89, Satisfactory: 60-74, Needs Improvement: 0-59)</instruction>
            </instructions>
        </section>

        <section id="key_strengths">
            <name>Key Strengths</name>
            <description>Identify 3-5 major strengths from across all evaluation sections</description>
            <instructions>
                <instruction>Focus on the highest-scoring elements from each evaluation section</instruction>
                <instruction>Prioritize strengths that contribute most significantly to the article's effectiveness</instruction>
                <instruction>Provide specific examples from the content to support each identified strength</instruction>
            </instructions>
        </section>

        <section id="priority_improvements">
            <name>Priority Improvements</name>
            <description>Identify 3-5 key areas for improvement from across all evaluation sections</description>
            <instructions>
                <instruction>Focus on the lowest-scoring elements from each evaluation section</instruction>
                <instruction>Prioritize issues that most significantly impact the article's effectiveness</instruction>
                <instruction>Provide specific, actionable recommendations for addressing each issue</instruction>
            </instructions>
        </section>

        <section id="section_summaries">
            <name>Section Summaries</name>
            <description>Provide brief summaries and scores for each evaluation section</description>
            <instructions>
                <instruction>Include the score for each section (0-100)</instruction>
                <instruction>Write a 1-2 sentence summary of key findings for each section</instruction>
                <instruction>List sections in order from highest to lowest score</instruction>
            </instructions>
        </section>
    </output_requirements>

    <output_format>
        <format>Markdown</format>
        <instructions>
            <instruction>Format your evaluation as a well-structured markdown document</instruction>
            <instruction>Use headers, lists, bold text, and other markdown elements for clarity</instruction>
            <instruction>Begin with the overall score prominently displayed</instruction>
            <instruction>Organize the content in the following order: Overall Score, Key Strengths, Priority Improvements, Section Summaries</instruction>
        </instructions>
    </output_format>

    <instructions>
        <instruction>Read all evaluation results carefully</instruction>
        <instruction>Extract scores from each section if available, or make reasonable estimates based on the qualitative feedback</instruction>
        <instruction>Focus on extracting actionable insights rather than general observations</instruction>
        <instruction>Prioritize items that would have the biggest impact on article performance</instruction>
        <instruction>Be concise but informative - the executive summary should be clear and to-the-point</instruction>
        <instruction>Return the evaluation as a professionally formatted markdown document</instruction>
    </instructions>
</prompt>
"""
    
    summary_result = llm.invoke(summary_prompt.format(result=combined_result)).content
    
    # Generate supplementary content improvement suggestions
    improvement_prompt = """
    <ImprovementRequest>
        <Role>
            You are an expert crypto content strategist specializing in Vietnamese market research.
        </Role>
        
        <Task>
            Based on the evaluation results, provide 3-5 specific content improvement suggestions 
            that would significantly enhance the article's quality and SEO performance.
            Focus on concrete examples and actionable advice.
        </Task>
        
        <Guidelines>
            <Guideline>Suggest specific sections or paragraphs that could be enhanced</Guideline>
            <Guideline>Provide examples of better phrasing or structure when possible</Guideline>
            <Guideline>Recommend additional content elements that would improve completeness</Guideline>
            <Guideline>Suggest SEO enhancements that align with Vietnamese search patterns</Guideline>
            <Guideline>Return suggestions in Vietnamese, formatted in Markdown</Guideline>
        </Guidelines>
        
        <Content>
        {result}
        </Content>
        
        <ArticleText>
        {text}
        </ArticleText>
    </ImprovementRequest>
    """
    
    improvement_suggestions = llm.invoke(improvement_prompt.format(result=combined_result, text=text)).content
    
    # Add improvement suggestions to the summary
    summary_result += "\n\n## Đề xuất cải thiện\n" + improvement_suggestions
    
    # Combine summary and detailed report
    final_result = f"""
# 📝 TÓM TẮT ĐÁNH GIÁ
{summary_result}

---

# 📋 BÁO CÁO CHI TIẾT
{detailed_result}
"""
    
    return final_result

if __name__ == "__main__":
    import os
    from langchain_openai import AzureChatOpenAI
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()

    # Initialize Azure OpenAI API with credentials and configuration
    llm = AzureChatOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        model="o3-mini",
        api_version="2024-12-01-preview",
    )

    text = "![Cover Image][width=1023,height=574][width=1023,height=574](https://statics.gemxresearch.com/images/2025/04/25/150501/real-world-assets-rwa-la-gi-ung-dung-cua-rwa-trong-defi.jpg) # Ứng dụng của RWA trong DeFi ## **Tổng quan&nbsp;** Thời gian qua, từ khóa [“**RWA**” – **Real World Assets**][rel=NO](https://gfiresearch.net/post/real-world-assets-rwa-la-gi-ung-dung-cua-rwa-trong-defi) (tài sản trong thế giới thực) đang được nhắc đến nhiều trên các nền tảng truyền thông. Đây được xem là xu hướng mới giúp thúc đẩy sự phát triển của thị trường DeFi sau một thời gian không có nhiều biến động.Vậy RWA là gì và có thể được ứng dụng như thế nào trong thị trường DeFi? Tất cả sẽ được tổng hợp trong bài viết dưới đây của [GFI Research][rel=NO](https://gfiresearch.net/). ## **Vì sao cần đưa RWA lên blockchain?&nbsp;** ### Thực trạng ảm đạm của thị trường DeFi&nbsp; Thị trường **DeFi** đã phát triển mạnh từ đầu năm 2020 và đạt mốc TVL hơn 180 tỷ USD vào cuối năm 2021. Kể từ đó, cùng với đà downtrend của thị trường, giá trị tài sản được khóa (TVL) trên các giao thức DeFi đã sụt giảm mạnh, chỉ còn dưới 50 tỷ USD.![][width=1050,height=449](https://statics.gemxresearch.com/images/2025/04/24/105916/thuc-trang-am-dam-cua-thi-truong-defi.jpg)  Vốn là trụ cột về tiến bộ công nghệ và là động lực phát triển của cả ngành blockchain, tuy nhiên hiện nay, DeFi vẫn mắc kẹt trong những mô hình tokenomics nghèo nàn với tỉ lệ lạm phát token cao.Một số token giảm hơn 90% giá trị, thậm chí biến mất khỏi thị trường, kéo theo lợi nhuận cho người dùng cũng giảm đáng kể. Lợi suất từ DeFi giờ chỉ còn tương đương với TradFi (Traditional Finance – tài chính truyền thống).Dễ thấy rằng TradFi cung cấp một mô hình đầu tư ít rủi ro hơn nhiều so với DeFi. Vậy khi lãi suất giữa hai mảng là như nhau, người dùng DeFi sẽ dần rút lui và trở về với TradFi. Thực trạng này đòi hỏi một nguồn lợi suất mới để vực dậy DeFi, và Real World Assets chính là câu trả lời. ### Động lực mới từ RWA&nbsp; Hiện nay, Real World Assets đang đóng góp một phần rất lớn vào giá trị của nền tài chính toàn cầu. Trong đó, thị trường nợ (với dòng tiền cố định) đã có giá trị khoảng 127 nghìn tỷ USD, thị trường bất động sản có giá trị khoảng 362 nghìn tỷ USD, và vốn hóa thị trường vàng là khoảng 11 nghìn tỷ USD.Trong khi đó, với TVL chỉ 50 tỷ USD, thị trường DeFi giống như một người tí hon so với vốn hóa của RWA. Nếu đưa được RWA lên blockchain, thị trường DeFi sẽ nhận được một dòng tài sản dồi dào những mô hình lợi nhuận đa dạng hơn, từ đó thúc đẩy tăng trưởng. ### DeFi mở ra tiềm năng khổng lồ cho RWA&nbsp; Không chỉ là bên được lợi từ Real World Assets, DeFi cũng giúp tạo ra một mô hình thị trường hiệu quả hơn, đặc biệt trong bối cảnh hiệu suất của TradFi đang dần bão hòa.TradFi đã phải phụ thuộc vào hệ thống trung gian từ ngày mới ra đời. Hệ thống trung gian gồm người môi giới, các hoạt động xác thực danh tính, và các quy định. Hệ thống này đã phần nào đảm bảo an toàn cho các giao dịch, nhưng đi kèm với đó là những hạn chế về hiệu quả sử dụng vốn.Theo Báo cáo ổn định tài chính toàn cầu 2022 của Quỹ Tiền tệ Quốc tế (IMF), TradFi kém hiệu quả vì người tham gia thị trường phải trả phí cho bên trung gian (gồm phí lao động và phí quản lý hệ thống).Ngoài ra, tài sản người dùng cũng bị kiểm soát bởi một bên thứ ba và đôi khi người dùng còn bị chặn khỏi hệ thống. Các mô hình DeFi sẽ giúp loại bỏ những hạn chế này này.Bên cạnh việc loại bỏ hệ thống trung gian, việc áp dụng DeFi vào RWA cũng giúp người dùng dễ dàng đa dạng hóa danh mục đầu tư thông qua các token. Thanh khoản cũng nhanh chóng với các mô hình AMM giúp người dùng ngay lập tức hoàn thành giao dịch.Đây là lợi ích cực kỳ lớn đối với những người đã quen với giao dịch chứng khoán. Nhà đầu tư chứng khoán thường phải liên hệ với công ty môi giới để giao dịch, và các giao dịch thường có độ trễ (như T+1, T+3).Một lợi ích cuối cùng của DeFi cho RWA chính là sự minh bạch của sổ cái blockchain, giúp người dùng quan sát được luồng giao dịch, từ đó đánh giá được tình hình thị trường. Những thông tin này thường bị giấu kín trong TradFi. ## **Ứng dụng của Real World Assets trong DeFi&nbsp;** Vậy khi Real World Assets được đưa lên blockchain, chúng sẽ được sử dụng như thế nào trong DeFi? Hiện nay, RWA có 3 ứng dụng chính trong DeFi:- Sử dụng làm **stablecoin**. - Tạo ra **synthetic token** (token tổng hợp). - Sử dụng làm tài sản trong các giao thức **lending**. ### Stablecoin Stablecoin là ví dụ hoàn hảo nhất của việc sử dụng RWA trong DeFi. USDT và USDC là 2 đồng stablecoin thường xuyên nằm trong top 5 token crypto hàng đầu theo vốn hóa thị trường, với tổng vốn hóa của chúng hiện đang ở mức hơn 110 tỷ USD. Điểm chung của cả hai là đều được đảm bảo bởi các tài sản thực như USD và trái phiếu.Hiện nay, USDC được đảm bảo peg 1:1 với USD nhờ kho tài sản dự trữ gồm 8,1 tỷ USD tiền mặt và 29 tỷ USD trái phiếu Kho bạc Hoa Kỳ. Tương tự, hơn 80% tài sản dự trữ của USDT là tiền mặt và trái phiếu Kho bạc, còn lại là trái phiếu doanh nghiệp, tiền cho vay và các khoản đầu tư khác.![][width=1050,height=993](https://statics.gemxresearch.com/images/2025/04/24/105957/usdc-duoc-dam-bao-boi-tien-mat-va-trai-phieu-kho-bac-hoa-ky.jpg)  Với tính chất này, các stablecoin là tài sản quan trọng của DeFi, hỗ trợ luân chuyển giá trị giữa thế giới thực và blockchain, cũng như là một tài sản trung gian để trú ẩn sự biến động của thị trường. ### Synthetic token&nbsp; Synthetic token hỗ trợ giao dịch on-chain cho các sản phẩm tài chính phái sinh liên quan đến tiền tệ, cổ phiếu và hàng hóa. Một nền tảng giao dịch synthetic token rất phổ biến là **Synthetix (SNX)** đã đạt mốc TVL gần 3 tỷ USD vào năm 2021.![][width=1050,height=393](https://statics.gemxresearch.com/images/2025/04/24/110017/tvl-cua-synthetix-tung-dat-hon-3-ty-usd.jpg)  Synthetic token có nhiều ứng dụng thú vị. Chẳng hạn, người nắm giữ tài sản thực như bất động sản có thể chứng khoán hóa dòng tiền từ hoạt động cho thuê, sau đó tokenize chứng khoán đó thành synthetic token để giao dịch trên DeFi. ### Lending&nbsp; Một số nền tảng lending như **Goldfinch**, **Maple Finance** hay **Centrifuge** giúp hỗ trợ vốn vay cho các doanh nghiệp trong thế giới thực. Các nền tảng này yêu cầu doanh nghiệp cung cấp các bằng chứng về tài sản và doanh thu, từ đó nhà đầu tư có thể cho các doanh nghiệp vay tiền một cách phi tập trung.Mô hình này cung cấp lợi nhuận tương đối ổn định và không chịu sự biến động của thị trường tiền điện tử. ## **Kết luận&nbsp;** **Real World Assets** là những tài sản ở thế giới thực được đưa lên blockchain nhằm tạo ra nguồn tài sản mới cho DeFi. DeFi cũng giúp người sở hữu RWA tối ưu hiệu quả sử dụng vốn so với TradFi.Một số ứng dụng nổi bật của RWA trong DeFi là stablecoin, synthetic token và lending. Đây chỉ là các ứng dụng đơn giản, do đó lĩnh vực này còn rất nhiều tiềm năng phát triển trong tương lai.Tuy nhiên, cũng phải để ý một số thách thức đặt ra cho RWA như **vấn đề định giá** và **xác thực cho tài sản**. Những bài viết tiếp theo của GFI Research sẽ đào sâu hơn về chủ đề này. ~~~metadata undefined: undefined undefined: undefined undefined: undefined Excerpt: undefined: undefined undefined: undefined Meta description: RWA” – Real World Assets (tài sản trong thế giới thực) thúc đẩy sự phát triển của thị trường DeFi sau một thời gian không có nhiều biến động. postUrl: ung-dung-cua-rwa-trong-defi ~~~"
    blog = text.split("~~~metadata")
    text = blog[0]
    metadata = blog[1][:-3]


    # print(check_content(llm,text))

    # print(check_methodology_objectivity(llm,text))

    # print(check_format_presentation(llm,text))

    # print(check_professional_technical(llm,text))

    print(check_seo(llm,text,metadata))

    # print(check_text(llm,text))