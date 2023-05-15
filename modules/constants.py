import os

BOT_NAME = "HeppaBOT"
SERVER_NAME = "HeppaSoft"
COMMAND_PREFIX = ".hb "
VERIFY_BUTTON_TEXT = "Doğrula"

ADMIN_ROLE = "Heppa"
CODER_ROLE = "Coder"
MODERATOR_ROLE = "Mod"
DEVELOPER_ROLE = "Developer"
VERIFY_ROLE = "HeppaSoft Üye"
UNIVERSITY_ROLE = "Üniversiteli"

EMBED_COLOUR = 16711680
EMBED_FOOTER = "İyi eğlenceler dileriz. HeppaSoft Yönetimi"
EMBED_AUTHOR_URL = ""
EMBED_AUTHOR_ICON_URL = "https://cdn.discordapp.com/avatars/938144508439302175/2afb01a5691f4253360a6b949196fd12.png?size=1024"
EMBED_AUTHOR_NAME = "HeppaSoft - HeppaBOT"

RANDOM_CODE_CHAR_SET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
RANDOM_CODE_LEN = 6

SENDEMAIL_FROM = "HeppaSoft"
SENDEMAIL_EMAIL_ADDRESS = os.getenv("SENDEMAIL_EMAIL_ADDRESS")
SENDEMAIL_EMAIL_PASSWORD = os.getenv("SENDEMAIL_EMAIL_PASSWORD")
SENDEMAIL_CONTENT = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Doğrulama</title>
  <!--[if mso]><style type="text/css">body, table, td, a { font-family: Arial, Helvetica, sans-serif !important; }</style><![endif]-->
</head>

<body style="font-family: Helvetica, Arial, sans-serif; margin: 0px; padding: 0px; background-color: #ffffff;">
  <table role="presentation"
    style="width: 100%; border-collapse: collapse; border: 0px; border-spacing: 0px; font-family: Arial, Helvetica, sans-serif; background-color: rgb(239, 239, 239);">
    <tbody>
      <tr>
        <td align="center" style="padding: 1rem 2rem; vertical-align: top; width: 100%;">
          <table role="presentation" style="max-width: 600px; border-collapse: collapse; border: 0px; border-spacing: 0px; text-align: left;">
            <tbody>
              <tr>
                <td style="padding: 40px 0px 0px;">
                  <div style="text-align: center;">
                    <div style="padding-bottom: 20px;"><img
                        src="https://cdn.discordapp.com/avatars/938144508439302175/2afb01a5691f4253360a6b949196fd12.png" alt="Company"
                        style="width: 89px;"></div>
                  </div>
                  <div style="padding: 20px; background-color: rgb(255, 255, 255);">
                    <div style="color: rgb(0, 0, 0); text-align: left;">
                      <h1 style="margin: 1rem 0">Merhaba {{name}},</h1>
                      <p style="padding-bottom: 16px">Ben {{bot_name}}, {{server_name}} Discord sunucusunda moderasyonu sağlamakla görevliyim.<br>Kısa bir
                        süre önce bir kullanıcı bu mail adresini kullanarak sunucuda kendisini onaylatmaya çalıştı.<br>Onaylanmayı sen talep
                        etmediysen bu maili görmezden gelebilirsin.</p>
                      <p style="padding-bottom: 16px">Başvuru kodun: <strong>{{verifaction_code}}</strong></p>
                      <p style="padding-bottom: 16px">Eğer başvuruyu sen gerçekleştirdiysen alt tarafta bulunan komutu
                        "{{channel}}" odasına yazabilirsin.</p>
                      <p style="padding-bottom: 16px">{{prefix}}başvuru_onay {{verifaction_code}}</p>
                      <p style="padding-bottom: 16px">Not: Bu isteği bir moderatör yardımı ile gerçekleştirdiysen bu kodu ona söylemen
                        yeterlidir.</p>
                      <p style="padding-bottom: 16px">İyi eğlenceler!<br>{{server_name}} Discord Yönetimi</p>
                    </div>
                  </div>
                  <div style="padding-top: 20px; color: rgb(153, 153, 153); text-align: center;">
                    <p style="padding-bottom: 16px">{{server_name}}</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </td>
      </tr>
    </tbody>
  </table>
</body>

</html>"""

SERVER_BOT_LOG_CHANNEL_ID = 940376132283433080
SERVER_BOT_MOD_CHANNEL_ID = 938143952018739200
SERVER_BOT_COMMAND_CHANNEL = 938514102433742978
SERVER_BOT_DEV_CHANNEL_ID = 1100151661290332235
SERVER_WELCOME_CHANNEL_ID = 1105104348582789140
SERVER_TICTACTOE_CHANNEL_ID = 1105120938619572324
SERVER_SUGGESTION_CHANNEL_ID = 938520660093853716
SERVER_ANNOUNCEMENT_CHANNEL_ID = 938518214332256286
SERVER_APPLICATIONS_CHANNEL_ID = 941304867195060234
SERVER_DEVELOPER_BOT_COMMAND_CHANNEL_ID = 1092836521792520212

MEMBER_DISCRIMINATOR_SIGN = "#"
SERVER_SUGGESTION_VOTES_APPROVAL = 10
LEVEL_METER_MESSAGE_EXP_POINT = 10

CHAT_BOT_SYSTEM_MESSAGE = "Adın HeppaBOT ve HeppaSoft Discord sunucusunda yönetimden sorumlu botsun. Üyeleri sunucudan banlıyabilir, atabilir; mesajlar gönderebilir, oyunlar oynuyabilir ve daha bir çok şey yapabilirsin. Yardım sayfası için komutun: \"{prefix}\" ."
