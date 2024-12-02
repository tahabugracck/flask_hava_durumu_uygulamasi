from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

# Flask uygulamasını başlatıyoruz
app = Flask(__name__)

# Şehir için hava durumu verilerini çeken fonksiyon
def weather(city):
    # Şehir için hava durumu web sayfasının URL'sini oluşturuyoruz
    link = f"https://havadurumu15gunluk.org/havadurumu/{city}-hava-durumu-15-gunluk.html"
    
    # Web sayfasına istek gönderip içeriğini alıyoruz
    data = requests.get(link).content
    # İçeriği BeautifulSoup ile parse ediyoruz. Düzenleme yapıyoruz
    data = BeautifulSoup(data, "html.parser")
    
    # Hava durumu bilgilerini içeren ana div'i buluyoruz
    data = data.find("div", {"class": "box weather"})

    try:
        # Hava durumu, sıcaklık ve hissedilen sıcaklık bilgilerini alıyoruz
        hava_durumu = data.find("span", {"class": "status"}).text.strip()
        sıcaklık = data.find("span", {"class": "temp high bold"}).text.strip()
        hissedilen = data.find("span", {"class": "temp low"}).text.strip()
        
        # Etiketler (rüzgar, nem vb.) verilerini alıyoruz
        etiketliler = data.find("ul").find_all("li")
        etiketler = [i.text.strip() for i in etiketliler]
        
        # Verileri döndürüyoruz
        return hava_durumu, sıcaklık, hissedilen, etiketler
    except AttributeError:
        # Eğer veriler bulunamazsa None döndürüyoruz
        return None, None, None, None

# Ana sayfa yönlendirmesi (GET ve POST isteklerini işliyoruz)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Kullanıcıdan gelen şehir adını alıyoruz
        city = request.form["city"]
        
        # Hava durumu verilerini alıyoruz
        hava_durumu, sıcaklık, hissedilen, etiketler = weather(city)
        
        # Eğer hava durumu verileri başarılı şekilde alınmışsa, bunları kullanıcıya gösteriyoruz
        if hava_durumu:
            return render_template("index.html", 
                                   city=city, 
                                   hava_durumu=hava_durumu, 
                                   sıcaklık=sıcaklık, 
                                   hissedilen=hissedilen, 
                                   etiketler=etiketler)
        else:
            # Eğer hava durumu verisi bulunamazsa hata mesajı gösteriyoruz
            error_message = "Hava durumu verisi bulunamadı. Lütfen şehir adını doğru girin."
            return render_template("index.html", error_message=error_message)

    # İlk yükleme sırasında ya da GET isteğiyle sayfayı render ediyoruz
    return render_template("index.html")

# Flask uygulamasını çalıştırıyoruz
if __name__ == "__main__":
    app.run(debug=True)
