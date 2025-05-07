
from openai import AzureOpenAI
import json
import time


class SirioPayloadAi:
    
    def __init__(self):
        self.payload = {
            'soggetto': None,
            'proposte': {},
            'assistente': {},
            'contesto': {'dati_da_analizzare': {}},
            'is_error': False
        }
        
    def setContesto(self, key:str, value):
        self.payload['contesto']['dati_da_analizzare'][key] = value

    def getContesto(self):
        return self.payload['contesto']

    def setAssistente(self, key:str, value):
        self.payload['assistente'][key] = value

    def setProposta(self, bind:str, id:str, value):
        self.payload.setdefault('proposte', {}).setdefault(bind, {}).setdefault(id, []).append(value)
    
    def getProposta(self, bind: str, id: str):
        return self.payload.get('proposte', {}).get(bind, {}).get(id, [])

    def getAllProposte(self):
        return self.payload.get('proposte', {})

    def setError(self, isError:bool):
        self.payload['is_error'] = isError

    def setSoggetto(self, soggetto:str):
        self.payload['soggetto'] = soggetto

    def getPayload(self):
        return self.payload

class ConfigAi:
    url_ai = ''
    ai_model = ''
    ai_temperature = 0.2
    ai_max_tokens = 4000
    ai_top_p = 0.95
    ai_frequency_penalty = 0
    ai_presence_penalty = 0
    ai_stop = None
    ai_model_rr1 = ''
    ai_model_rr2 = ''
    ai_model_rr3 = ''
    api_key = ''
    api_version = ''
    def __init__(self, url_ai: str, ai_model: str, 
                ai_temperature: float, ai_max_tokens: float,  
                ai_top_p: float, ai_frequency_penalty: float, 
                ai_presence_penalty: float, 
                ai_stop , ai_model_rr1: str,
                ai_model_rr2: str, ai_model_rr3 : str, 
                api_key: str, api_version: str):
        self.url_ai = url_ai
        self.ai_model = ai_model
        self.ai_temperature = ai_temperature
        self.ai_max_tokens = ai_max_tokens
        self.ai_top_p = ai_top_p
        self.ai_frequency_penalty = ai_frequency_penalty
        self.ai_presence_penalty = ai_presence_penalty
        self.ai_stop = ai_stop
        self.ai_model_rr1 = ai_model_rr1
        self.ai_model_rr2 = ai_model_rr2
        self.ai_model_rr3 = ai_model_rr3
        self.api_key = api_key
        self.api_version = api_version

class SirioAi:
    config: ConfigAi
    client: AzureOpenAI
    def __init__(self, config: ConfigAi ):
        self.config = config
        self.client = AzureOpenAI(
                azure_endpoint = self.config.url_ai,
                api_key = self.config.api_key,
                api_version = self.config.api_version
            )

    def invocaGPT(self, numero_risposta, domanda, assistente, esempio, dati):
        start_time = time.perf_counter()
        """
        message_text = [
            {"role": "system", "content": assistente},
            {"role": "user", "content": domanda + " " + json.dumps(dati)},
            {"role": "assistant", "content": esempio},
            {"role": "user", "content": domanda},
        ]
        """
        message_text = [
            {"role": "system", "content": f"{assistente} Rispondi seguendo lo schema dell'esempio fornito." if esempio else f"{assistente} Rispondi in modo chiaro e preciso."},
            {"role": "user", "content": f"Domanda: {domanda}\nDati:\n{json.dumps(dati, indent=2)}"}
        ]

        if esempio:  # Se esiste un esempio, lo aggiunge al messaggio
            message_text.append({"role": "assistant", "content": f"Esempio di risposta:\n{esempio}"})

        risposta = self._invocaGPT(message_text)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        kpi = f'{elapsed_time:.4f}'
        jsonReturn = {"numero_risposta": str(numero_risposta),  "risposta" : risposta, "kpi": kpi}
        return jsonReturn
    
    def invocaGPTSimple(self, numero_risposta, domanda, assistente):
        start_time = time.perf_counter()
        message_text = [
                {"role": "system", "content": assistente},
                {"role": "user", "content": "rispondi con il solo json " + domanda}
            ]
        
        risposta = self._invocaGPT(message_text)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        kpi = f'{elapsed_time:.4f}'
        jsonReturn = {"numero_risposta": str(numero_risposta),  "risposta" : risposta, "kpi": kpi}
        return jsonReturn
    
    def invocaGPTRaw(self, numero_risposta, prompt):
        start_time = time.perf_counter()
        
        risposta = self._invocaGPT(prompt)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        kpi = f'{elapsed_time:.4f}'
        jsonReturn = {"numero_risposta": str(numero_risposta),  "risposta" : risposta, "kpi": kpi}
        return jsonReturn
    
    def _invocaGPT(self, prompt):
        complete = False
        risposta = None
        while not complete:
            try:
                completion = self.client.chat.completions.create(
                    model = self.config.ai_model,
                    messages=prompt,
                    temperature = float(self.config.ai_temperature),
                    max_tokens = int(self.config.ai_max_tokens),
                    top_p = float(self.config.ai_top_p),
                    frequency_penalty = int(self.config.ai_frequency_penalty),
                    presence_penalty = int(self.config.ai_presence_penalty),
                    stop = self.config.ai_stop
                )

                #self.l.log("Testo Generato: " + completion.choices[0].message.content, level=logging.INFO)
                risposta = completion.choices[0].message.content
                complete = True
            
            except Exception as e:
                if "rate limit" in str(e).lower():
                    retry_after = 2
                    print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    print(f"HTTP error: {e}")
                    raise
        return risposta

