# 🧠 AI Health Diary

AI Health Diary, kullanıcıların sağlık durumlarını takip etmelerine ve yapay zeka desteğiyle daha kapsamlı analizler yapmalarına olanak tanıyan bir kişisel sağlık günlüğü uygulamasıdır.

## Özellikler
- Kullanıcılar sağlıkla ilgili günlük girdiler oluşturabilir.
- Gemini destekli yapay zeka ile bu girdiler açıklamalı ve analizli hale getirilir.
- JWT tabanlı kullanıcı kimlik doğrulama.
- FastAPI tabanlı backend.

## Kurulum
1. Python 3.11 veya üstü yüklü olduğundan emin olun.
2. Aşağıdaki adımları izleyin:

```bash
git clone <repo-url>
cd ai-health-diary
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. `.env` dosyasını proje kök dizinine oluşturun ve Gemini API anahtarınızı ekleyin:

```
ÖRNEK KULLANIM:
GOOGLE_API_KEY="hıbewfıwjfefsgf25snwehr"
```

4. Uygulamayı başlatın:

```bash
uvicorn main:app --reload
```
