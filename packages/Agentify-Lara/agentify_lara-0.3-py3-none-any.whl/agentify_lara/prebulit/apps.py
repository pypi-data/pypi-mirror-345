class Translator():
    def __init__(self,llm,lang:str):
        self.__llm=llm
        self.lang=lang

        from langchain_core.pydantic_v1 import BaseModel
        class translator(BaseModel):
            from langchain_core.pydantic_v1 import Field
            text:str=Field('input user')
            translated_text:str=Field(f'translate the text in to {self.lang}')

    def invoke(self,text:str):
        self.__llm.with_structure_output(translator).invoke(text)
    
