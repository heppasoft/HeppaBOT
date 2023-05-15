# Changelog
Bu projedeki tüm önemli değişiklikler bu dosyada belgelenecektir.

Biçim, ["Keep a Changelog"](https://keepachangelog.com/tr-TR/1.1.0/) 'a dayalıdır,
ve bu proje ["Semantic Versioning"](https://semver.org/lang/tr/spec/v2.0.0.html) ile uyumludur.


## [1.2.2] - 15-05-2023

### [Değişti]

- `modules/constants.py` dosyasında gizlilik için değişiklikler yapıldı.

### [Kaldırıldı]

- Gereksiz dosyalar kaldırıldı.

## [1.2.1] - 13-05-2023

### [Eklendi]

- Bot ile sohbet edebilmek için yeni Openai API kullanılarak ChatBot özelliği eklendi.
- Yönetim komutlarına ChatBot mesaj geçmişini temizlemek için komut eklendi.
- Yönetim komutlarına sunucudaki tüm kanalları temizlemek için komut eklendi.

### [Değişti]

- Bir hata oluşunca kullanıcıya bildirme özelliği düzenlenip aktif edildi.
- Hata sınıfları için ana sınıf oluşturulup kullanıldı.
- Bot sınıfındaki yanlış kanal ve eksik rol hata bildirimleri event çağırılacak şekilde yeniden düzenlendi.

### [Düzeltildi]

- `TicTacToe` oyunu özelliğindeki hatalar giderildi.
- `compiler` özelliğindeki hatalar giderildi.

## [1.1.1] - 08-05-2023

### [Eklendi]

- `TicTacToe` oyunu özelliği eklendi.
- Geliştirme aşamasında kolaylık sağlaması için 2 yeni komut eklendi.

### [Değişti]

- Derleyicinin desteklenen dilleri ve derleyicileri güncelleme işlemlerinde düzeltmeler yapıldı.
- Ufak genel yazım düzeltmeleri yapıldı.

## [1.0.0] - 08-05-2023
Discord botunun ilk sürümüdür.
