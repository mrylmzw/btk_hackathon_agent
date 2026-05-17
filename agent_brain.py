import os
# Gerekli olan eksik import satırımız:
from langchain_core.prompts import PromptTemplate
from langchain_classic import hub
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from agent_tools import get_agent_tools

# 1. API Anahtarı Kontrolü
# Eğer terminalden 'set' etmediyseniz, aşağıdaki satırın yorum satırını kaldırıp anahtarınızı yazabilirsiniz:
# os.environ["GEMINI_API_KEY"] = "AIzaSy..."
# KODUN BAŞINA DOĞRUDAN EKLEYİN:
os.environ["GEMINI_API_KEY"] = "AIzaSyBtWhPzT3tYkldFjBBDjxZDLKdGZTzJ92c"

if "GEMINI_API_KEY" not in os.environ or os.environ["GEMINI_API_KEY"].startswith("AIzaSyYour"):
    print("[Hata] Lütfen os.environ[\"GEMINI_API_KEY\"] alanına kendi gerçek API anahtarınızı yazın!")
    exit()

print("[Beyin] Gemini 2.5 Flash modeli hazırlanıyor...")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.1  # Tutarlılık ve katı format uyumu için düşük sıcaklık
)

print("[Sistem] Yerel ReAct Prompt şablonu yükleniyor...")
react_template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

react_prompt = PromptTemplate.from_template(react_template)

print("[Ajan] ReAct Ajanı oluşturuluyor...")
agent = create_react_agent(llm, get_agent_tools, react_prompt)

agent_executor = AgentExecutor(
    agent=agent, 
    tools=get_agent_tools, 
    verbose=True, 
    handle_parsing_errors=True 
)

if __name__ == "__main__":
    print("\n=== AGENT 1: DUE DILIGENCE RISK ANALİZİ (FAZ 6) BAŞLADI ===")
    
    # Yeni Katı ve Detaylı JSON Şeması Promptu
    user_query = (
        "Analyze the uploaded company records using your search tools. "
        "Identify critical patent infringements, legal lawsuits, and analyze financial health (liquidity, debt, purchase obligations). "
        "\n\n"
        "CRITICAL RULE: Your Final Answer MUST be ONLY a raw JSON string. Do not wrap it in markdown code blocks like ```json. "
        "The JSON structure must strictly follow this exact schema:\n"
        "{\n"
        "  'legal_risks': [\n"
        "    {\n"
        "      'risk_summary': 'Clear description of the lawsuit or patent issue',\n"
        "      'severity': 'High' or 'Medium' or 'Low',\n"
        "      'risk_score': 1 to 10 (integer),\n"
        "      'source_quote': 'The exact or core sentence from the document text showing this risk',\n"
        "      'location': 'The specific item or section name where it was found (e.g., Item 1A, Item 3)'\n"
        "    }\n"
        "  ],\n"
        "  'financial_risks': [\n"
        "    {\n"
        "      'risk_summary': 'Clear description of the debt, liquidity or commitment issue',\n"
        "      'severity': 'High' or 'Medium' or 'Low',\n"
        "      'risk_score': 1 to 10 (integer),\n"
        "      'source_quote': 'The exact or core sentence/metrics from the text showing this financial risk',\n"
        "      'location': 'The specific item or section name (e.g., Item 7)'\n"
        "    }\n"
        "  ],\n"
        "  'm_and_a_summary': 'Your overall senior M&A expert executive overview summarizing the target company risk profile.'\n"
        "}"
    )
    
    # Ajanı tetikliyoruz
    response = agent_executor.invoke({"input": user_query})
    
    print("\n=== AJANIN NİHAİ YAPILANDIRILMIŞ RAPOR ÇIKTISI (FAZ 6) ===")
    print(response["output"])