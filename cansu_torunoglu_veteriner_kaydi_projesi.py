import datetime
import pandas as pd
import requests
import io

class Asi_Takvimi:
    def __init__(self):
        
        self.yetiskin_asilar = {
            'iç-dış parazit': 60,
            'karma': 365,
            'lösemi': 365,
            'bronşit': 365,
            'korona': 365,
            'kuduz': 365
        }
        
        self.yavru_kedi_asilar = {
            'iç-dış parazit': 60,
            'karma': 14,
            'lösemi': 14,
            'bronşit': 14,
            'korona': 14,
            'kuduz': 365
        }
        
        self.yavru_kopek_asilar = {
            'iç-dış parazit': 60,
            'karma': 21,
            'bronşit': 21,
            'korona': 21,
            'kuduz': 365
        }

    def Asi(self, hayvan_tipi, yas_durumu):

        tip = hayvan_tipi.strip().lower()
        yas = yas_durumu.strip().lower()

        if yas == 'yetişkin':
            uygulanacak_asilar = self.yetiskin_asilar.copy()
            if tip == 'köpek':
                uygulanacak_asilar.pop('lösemi', None)
            return uygulanacak_asilar

        return self.yavru_kedi_asilar.copy() if tip == 'kedi' else self.yavru_kopek_asilar.copy()

    def sonraki_asitarihi(self, son_tarih, aralik_gun):

        duzeltme = son_tarih.replace('.', '-').replace('/', '-')
        try:
            tarih = datetime.datetime.strptime(duzeltme, '%d-%m-%Y')
        except ValueError:
            return 'Hatalı tarih formatı'
        return (tarih + datetime.timedelta(days=aralik_gun)).strftime('%d-%m-%Y')

    def asi_durumu(self, hayvan_tipi, yas_durumu, gecmis_asilar):

        ihtiyac = self.Asi(hayvan_tipi, yas_durumu)
        tamamlanan = []
        eksik = []

        for asi, aralik in ihtiyac.items():
            if asi in gecmis_asilar:
                dozlar = gecmis_asilar[asi]
                son = dozlar[-1]
                if asi == 'iç-dış parazit':
                    sonraki = self.sonraki_asitarihi(son, 60)
                elif asi == 'kuduz':
                    sonraki = self.sonraki_asitarihi(son, 365)
                else:
                    if len(dozlar) < 2:
                        sonraki = self.sonraki_asitarihi(son, aralik)
                    else:
                        sonraki = self.sonraki_asitarihi(son, 365)
                tamamlanan.append(f"{asi} – Yapıldı ({son}) – Sonraki: {sonraki}")
            else:
                ası_eksik = 'EKSİK' if yas_durumu.strip().lower() == 'yetişkin' else ' DOZ EKSİK'
                eksik.append(f"{asi} – {ası_eksik}")

        print("\nYAPILAN AŞILAR:")
        for yapilan_asi in tamamlanan:
            print("  •", yapilan_asi)

        print("\nEKSİK AŞILAR:")
        for eksik_asi in eksik:
            print("  •", eksik_asi)


class Analiz:
    def __init__(self):
        
        self.dog_file = 'https://github.com/CansuTorunoglu/veterinerlik_kaydi_otomatiklesmis_sistem/raw/refs/heads/main/kopek_boy_kilo.csv'
        self.cat_file = 'https://github.com/CansuTorunoglu/veterinerlik_kaydi_otomatiklesmis_sistem/raw/refs/heads/main/kedi_boy_kilo.csv'
        self.disease_file = 'https://github.com/CansuTorunoglu/veterinerlik_kaydi_otomatiklesmis_sistem/raw/refs/heads/main/kedi_kopek_hastalik.xlsx'
        self.veri_yukleme()

    def veri_yukleme(self):
        try:
            self.dog_data = pd.read_csv(self.dog_file, delimiter=';', on_bad_lines='skip')
            self.cat_data = pd.read_csv(self.cat_file, delimiter=';', on_bad_lines='skip')

            sonuc = requests.get(self.disease_file)
            sonuc.raise_for_status()
            self.disease_data = pd.read_excel(io.BytesIO(sonuc.content), sheet_name='Sayfa1')

            self.dog_breeds = sorted(set(self.dog_data['Breed'].dropna()) & set(self.disease_data['Breed'].dropna()))
            self.cat_breeds = sorted(set(self.cat_data['name'].dropna()) & set(self.disease_data['Breed'].dropna()))
        except Exception as hata:
            print(f"Yükleme hatası: {hata}")


    def Hayvan_Bilgileri(self):
        info = {}
        try:
            info['İsim'] = input("Hayvanın ismi: ").strip()
            info['Cinsiyet'] = input("Cinsiyet (Erkek/Dişi): ").strip().title()
            info['Kısır'] = input("Kısır mı? (Evet/Hayır): ").strip().title()
            info['Alerji'] = input("Alerjisi var mı? (Evet/Hayır): ").strip().title()
            if info['Alerji'] == 'Evet':
                info['Alerji Detay'] = input("Alerji detayları: ").strip()
            info['İlaç'] = input("İlaç kullanıyor mu? (Evet/Hayır): ").strip().title()
            if info['İlaç'] == 'Evet':
                info['İlaç Detay'] = input("İlaç isimleri: ").strip()
            info['Ameliyat'] = input("Ameliyat oldu mu? (Evet/Hayır): ").strip().title()
            if info['Ameliyat'] == 'Evet':
                info['Ameliyat Detay'] = input("Ameliyat detayları: ").strip()
        except Exception:
            print(" Hata ")
        print("\n--- HAYVAN BİLGİLERİ ALINDI ---")
        return info

    def hayvan_ve_irki(self):
        kind = input("Kedi mi Köpek mi? (Kedi/Köpek): ").strip().title()
        breeds = self.cat_breeds if kind == 'Kedi' else self.dog_breeds if kind == 'Köpek' else []
        while not breeds:
            print(f"{kind} için ırk bulunamadı.")
            kind = input("Kedi mi Köpek mi? (Kedi/Köpek): ").strip().title()
            breeds = self.cat_breeds if kind == 'Kedi' else self.dog_breeds
        print(f"Kesişen {kind} Irkları: {breeds}")
        breed = input("Irkı seçiniz: ").strip().title()
        while breed not in breeds:
            print("Geçersiz ırk. Tekrar deneyin.")
            breed = input("Irkı seçiniz: ").strip().title()
        return kind, breed

    def Asi_Hatirlaticisi(self):
        print("\n--- AŞI HATIRLATICISI ---")
        takvim = Asi_Takvimi()
        kind, breed = self.hayvan_ve_irki()
        print(f"Seçilen ırk: {breed}")
        yas_grubu = input("Yaş grubu (Yavru/Yetişkin): ").strip().title()
        gerekli_asilar = takvim.Asi(kind, yas_grubu)
        gecmiş_asilar = {}
        print("Mevcut Aşılar:")
        for i, asi in enumerate(gerekli_asilar, 1):
            print(f"{i}. {asi}")
        print("Aşı geçmişi giriniz (bitir 'q'):")
        while True:
            secim = input("Aşı seç (numara/isim): ").strip()
            if secim.lower() == 'q':
                break
            if secim.isdigit():
                secim_numarası = int(secim) - 1
                if secim_numarası < 0 or secim_numarası >= len(gerekli_asilar):
                    print("Geçersiz seçim. Lütfen tekrar deneyin.")
                    continue
                secilen_asi = list(gerekli_asilar.keys())[secim_numarası]
            else:
                if secim not in gerekli_asilar:
                    print("Geçersiz seçim. Lütfen tekrar deneyin.")
                    continue
                secilen_asi = secim
            date = input(f"{secilen_asi} tarihi (DD-MM-YYYY): ").strip()
            gecmiş_asilar.setdefault(secilen_asi, []).append(date)
        takvim.asi_durumu(kind, yas_grubu, gecmiş_asilar)

    def Kilo_kontrol(self):
        print("\n--- KİLO KONTROLÜ ---")
        kind, breed = self.hayvan_ve_irki()
        df = self.cat_data if kind == 'Kedi' else self.dog_data
        if kind == 'Kedi':
            alt_sinir, ust_sinir = df.loc[df['name'] == breed, ['min_weight', 'max_weight']].astype(float).iloc[0]
        else:
            alt_sinir, ust_sinir = df.loc[df['Breed'] == breed, ['weight_low_lbs', 'weight_high_lbs']].astype(float).iloc[0]
        while True:
            kilo_girisi = input("Kilo giriniz (numeric): ").strip()
            try:
                kilo = float(kilo_girisi)
            except ValueError:
                print("Geçersiz kilo değeri. Tekrar deneyin.")
                continue
            if kilo < alt_sinir:
                print("Kilo düşük.")
            elif kilo > ust_sinir:
                print("Kilo fazla.")
            else:
                print("Kilo normal.")
            break

    def Hastalik_eslesmesi(self):
        print("\n--- BELİRTİ & TANILAR ---")
        kind, breed = self.hayvan_ve_irki()
        ceviri = {'Köpek': 'Dog', 'Kedi': 'Cat'}
        kind = ceviri.get(kind)
        if not kind:
            print(f"Bilinmeyen hayvan türü: {kind}")
            return

    
        df = self.disease_data[
            (self.disease_data['Breed'] == breed.strip().title()) &
            (self.disease_data['Animal_Type'] == kind)
        ]

    
        semptoms = {
        'Appetite_Loss':      'İştah Kaybı',
        'Vomiting':           'Kusma',
        'Diarrhea':           'İshal',
        'Coughing':           'Öksürük',
        'Labored_Breathing':  'Zor Nefes Alma',
        'Lameness':           'Topallama',
        'Skin_Lesions':       'Cilt Lezyonları',
        'Nasal_Discharge':    'Burun Akıntısı',
        'Eye_Discharge':      'Göz Akıntısı'
    }
        kullanici_belirtileri = {}
        for belirti , aciklama in semptoms.items():
            while True:
                giris = input(f"{belirti} ({aciklama}) (Yes/No): ").strip().lower()
                if giris in ('yes','y','no','n'):
                    kullanici_belirtileri[belirti] = 'Yes' if giris.startswith('y') else 'No'
                    break
                print("Geçersiz giriş. Yes veya No giriniz.")

        for belirti in semptoms:
            if belirti in df.columns:
                df = df[df[belirti] == kullanici_belirtileri[belirti]]

        tahmin = df['Disease_Prediction'].dropna().unique().tolist()
        if tahmin:
            print("Olası Hastalıklar:", tahmin)
        else:
            print("Belirtilere uygun hastalık bulunamadı.")
    def run(self):
       
        self.hayvan_bilgileri = self.Hayvan_Bilgileri()
        while True:
            print("\n--- ANA MENÜ ---")
            print("1 - Aşı Hatırlatıcısı")
            print("2 - Kilo Değerlendirmesi")
            print("3 - Belirti-Hastalık Eşleştirme")
            print("4 - Çıkış")
            ilk_secim = input("Seçiminiz: ").strip()
            if ilk_secim == '1':
                self.Asi_Hatirlaticisi()
            elif ilk_secim == '2':
                self.Kilo_kontrol()
            elif ilk_secim == '3':
                self.Hastalik_eslesmesi()
            elif ilk_secim == '4':
                print("Programdan çıkılıyor...")
                break
            else:
                print("Geçersiz seçim. Tekrar deneyin.")

if __name__ == '__main__':
    app = Analiz()
    app.run()  


