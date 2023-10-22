from langchain.llms import GooglePalm
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

#llm = GooglePalm(modelName="models/text-bison-001")
llm = ChatOpenAI(temperature=0)
system_prompt = ""
with open("prompt.txt", 'r') as prompt_fh:
    system_prompt = prompt_fh.read()

print(system_prompt + "\n{question}")
prompt_template = PromptTemplate(
    input_variables=["question"],
    template= system_prompt + "\n{question}",
)
chain = LLMChain(llm=llm, prompt=prompt_template)

question = "create configuration for iot_sensors - device_id is integer between 100 and 999, device_name is a string of 10 characters, factory_id - which ranges from 1 to 10, section which has value randomly selected from  [A B C D], sensor_type which is one of [ temperature humidiuty proximity smoke level ], date_commisioned is past date upto 5 years old with reference date of 01-01-2018. Application should create records dynamically."

resp = chain.run(question=question)
print(resp)