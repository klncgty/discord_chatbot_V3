import discord
import os
import re
import openai
from datetime import datetime
from discord.ext import commands
from discord import Interaction
from langchain.memory import ConversationBufferMemory
from anahtar_kelimeler import A
from discord import Intents, Client, Message
import asyncio
import json
from dotenv import load_dotenv
from discord import File
from easyocr import Reader
from PIL import Image
import aiohttp
import extract
import fetch



load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
openai.api_key = os.getenv('GPT_API_KEY')


SYSTEM_PROMPT = {"role": "system", "content": "Sen veri bilimci, veri analisti, veri mühendisi,sanal makine kurulumu,  makine öğrenmesi ,sanal makine, sanal makina, front end,robotik, django,laravel, game development, web scrapping, uı/ux"
"konularında uszman bir eğitim rehberisin. Şuan MIUUL isimli veribilimi eğitimi veren bir kurumda," 
" öğrencilerin sorularını cevaplayan bir yardımsever bir asistansın."
" Eğer sana veri bilimi, python, sanal makine, sanal makina, front end,robotik, django,laravel,  game development, web scrapping, uı/ux,  makine öğrenmesi,veri analisti,veri mühendisi alanında sorular sorulursa cevapla. bu konular dışında bir soru sorulursa, sadece uzmanı olduğum "
"bu konular hakkında cevap verebileceğini nazik bir dille belirt. Çok kısa cümlelerle cevap ver. ve cümle sonlarına, son kurduğun cümleye uygun  emoji koy." }

image_text=None



MAX_TOKENS = 200
TEMPERATURE = 0.3
N=1
FREQUENCY_PENALTY = 0.9
PRESENCE_PENALTY = 0.0
MODEL = "gpt-4"


def kaydet(soru, cevap):
    tarih = datetime.now()

    data = {
        "soru": soru,
        "cevap": cevap,
        "tarih": tarih.strftime("%Y-%m-%d %H:%M:%S")
    }

    if not os.path.exists("sorular.json"):
        with open("sorular.json", "w") as f:
            json.dump(f)
    with open("sorular.json", "a") as f:
        json.dump(data, f)

intents: Intents = discord.Intents.all()
intents.message_content=True
intents.reactions = True



memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


client: Client = Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user.name} olarak giriş yapıldı')



@client.event
async def on_message(message):
    
        
    channel = message.channel
    content = message.content.lower()
    
    if message.author == client.user:
        return
    
   
    
    """
    İSTENİLEN SAATTE ÇALIŞMASI İÇİN
    
    """
    #current_time = datetime.now().time()
    #if not (datetime.strptime('22:00:00', '%H:%M:%S').time() <= current_time <= datetime.strptime('08:00:00', '%H:%M:%S').time()):
        #return
    if not message.content.startswith("/"):
        return
    if message.attachments:  # Eğer mesaj ekleri varsa
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
            # Eğer ek resim dosyası ise
                image_url = attachment.url
                image_bytes = await fetch.fetch_image_data(image_url)
                text_result = extract.extract_text_from_image(image_bytes)
                content_with_image = f"{content} {text_result} ."
                gpt_answer_combined = gpt_cevap_al(content_with_image)
                await channel.send(f"{message.author.mention}, {gpt_answer_combined}")
                #sum_text = hatayı_özetle(text_result)
                #kaydet(sum_text,gpt_answer)
                
                break
            
    elif any(keyword in content for keyword in ["fiyat", "ücret", "miuul"]):
        await channel.send(f"{message.author.mention} Miuul Eğitimleri ile ilgili mentorlerimize direkt mesaj yoluyla danışabilirsiniz :)")
        await channel.send("Detaylı bilgi için Miuul Bootcamp kataloğunu inceleyebilirsiniz: [Miuul Katalog](https://miuul.com/katalog?tur=bootcamp)")

    elif "path" in content and "bootcamp" in content:
        await channel.send(f"{message.author.mention} Bootcamp programında program öncesi ön hazırlık eğitimi, canlı mentor desteği, Vahit Keskin ile birlikte haftalık recap, takım çalışması ve IK ve teknik mülakatlar gibi içerikler mevcuttur.")
        await channel.send("[MIUUL](https://www.miuul.com/)'a tıklayarak tüm detaylara ulaşabilirsiniz. Daha detaylı bilgiler için mentorlerimizden de destek alabilirsiniz :)")

    elif "bootcamp" in content:
        await channel.send(f"{message.author.mention} Bootcamp programında program öncesi ön hazırlık eğitimi, canlı mentor desteği, Vahit Keskin ile birlikte haftalık recap, takım çalışması ve IK ve teknik mülakatlar gibi içerikler mevcuttur.")
        await channel.send("Miuul Bootcamp kataloğunu inceleyebilirsiniz: [Miuul Bootcamp Kataloğu](https://miuul.com/katalog?tur=bootcamp)")

    elif "path" in content:
        await channel.send(f"{message.author.mention} Path programında eğitimler tekildir ve kendi öğrenme hızınıza göre takip ediyor olacaksınız. Tüm içeriklere 1 yıl erişim hakkınız bulunmaktadır. Sorularınız olması durumunda da mentorlarımız ile 7/24 iletişim kurarak süreci ilerletiyor olacaksınız.")
        await channel.send("Bu linkten Miuul Path kataloğunu inceleyebilirsiniz: [Miuul Path Kataloğu](https://www.miuul.com/katalog?tur=kariyer&gclid=CjwKCAjw9-6oBhBaEiwAHv1QvKewPIfjJ78iUKuZGDVMbO5MZDFINlIG62Yssx8rcEmw0jiqH1Tv1RoC24QQAvD_BwE)")

    elif "teşekkür" in content:
        await channel.send(f" {message.author.mention} Ne demek, rica ederim. İyi çalışmalar! :)")
        
    elif any(kelime.lower() in content for kelime in A):
        num_authors = len(set([author.id for author in message.mentions]))
        
        if num_authors > 1:
            await asyncio.sleep(3)
        await channel.send(f"{message.author.mention} Cevabınızı düşünüyorum!")
        gpt_answer = gpt_cevap_al(content)
        await message.reply(f"{message.author.mention} {gpt_answer}")
        
        kaydet(content,gpt_answer)
        

    elif "selam" in content or "naber" in content or "merhaba" in content:
        await channel.send(f" {message.author.mention} Merhaba! Ben Miuul yapay zeka botuyum. Size nasıl yardımcı olabilirim :) ")
            
            
    elif "cake" in content:
        await channel.send(f" {message.author.mention} Olsa da yesek be ")

    
            
            
    else:
        await channel.send(f"{message.author.mention} Ben Miuul path yapay zeka botuyum. Bu konularda sorunuz varsa size yardımcı olmayı çok isterim.")


def gpt_cevap_al(content,image_text=None):
    
    if image_text is not None:
        combined_text = content + " " + image_text
    else:
        combined_text = content
    
    try:
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=memory.chat_memory.messages + [
                    SYSTEM_PROMPT,
                    {"role": "user", "content": combined_text}
                    
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                stop="Umarım yardımcı olabilmişimdir. Daha detaylı bilgi için mentor arkadaşlarıma DM üzerinden de soru sormaya çekinmeyin lütfen",
                n=N,
                frequency_penalty=FREQUENCY_PENALTY,
                presence_penalty=PRESENCE_PENALTY
            )
            
            memory.chat_memory.messages.append(
                {'role': 'system', 'content': response["choices"][0]["message"]["content"]})
            print(response)
            
            answer = response["choices"][0]["message"]["content"]
            return answer
        
    except Exception as e:
                print(e)
                return " gpt'de problem var!!!"
"""
EĞER EKRAN GÖRÜNTÜSÜNÜN ÖZETİNİ GEREKİRSE BUNLARI AKTİF ET"""    
      
#from transformers import pipeline
#prompt_text = f"{text_result} Bu hatanın ne olduğunu türkçe olarak bir cümlede özetle:"

#def hatayı_özetle(text):
    #summarizer = pipeline("summarization", model="tuner007/pegasus_paraphrase")

    #summary = summarizer(text, max_length=100, min_length=5, do_sample=False)

    #summarized_text = summary[0]['summary_text']

    #return summarized_text           
            




client.run(TOKEN)


