#!/usr/bin/env python

"""Tests for `sirio` package."""


import unittest
import io


from sirio import event

from   sirio.business_object import BusinessObject, Object

from sirio.service import SirioService

from sirio.sirio_ai import ConfigAi, SirioAi, SirioPayloadAi

config = ConfigAi(url_ai = 'https://openai-gpt4-cerved.openai.azure.com/', 
                  ai_model = 'Gpt4o-1', 
                  ai_temperature = 0.2,
                  ai_max_tokens = 4000,
                  ai_top_p = 0.95,
                  ai_frequency_penalty = 0,
                  ai_presence_penalty = 0,
                  ai_stop = None,
                  ai_model_rr1 = 'Gpt4o-1',
                  ai_model_rr2 = 'Gpt4o-2',
                  ai_model_rr3 = 'Gpt4o-3',
                  api_key = '339d9b2cf2e8442d93cc27a138b3f068',
                  api_version = '2024-02-15-preview')

payload = SirioPayloadAi()
gpt = SirioAi(config)
domanda = "Come sta il pontefice"
esempio = ''
assistente = 'Cerca di essere rassicurante, e di trasmettere speranza.'
bollettino = {'bollettino_medico':'Bollettino medico di sabato 8 marzo 2025: Il pontefice rimane in prognosi riservata. Le sue condizioni sono stabili, ma gravi'}
payload.setContesto(key='bollettino_medico', value=bollettino)
risposta = gpt.invocaGPT(1,domanda=domanda,assistente=assistente, esempio=esempio, dati=payload.getContesto() )
payload.setProposta(bind='proposte',id='prima', value=risposta)


print(payload.getPayload())



class TestSirio(unittest.TestCase):
    """Tests for `sirio` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

