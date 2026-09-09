package vn.tubinh.sotay;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.util.Base64;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.zip.GZIPInputStream;

public class MainActivity extends Activity {
    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.rgb(23, 18, 16));
        getWindow().setNavigationBarColor(Color.rgb(23, 18, 16));

        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(23, 18, 16));
        setContentView(web);

        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setTextZoom(100);

        web.setWebViewClient(new WebViewClient());
        web.setWebChromeClient(new WebChromeClient());
        web.loadDataWithBaseURL("https://local.tubinh.vn/", personalizeHtml(loadHtml()), "text/html", "UTF-8", null);
    }

    private String personalizeHtml(String html) {
        html = html.replace("<title>Sổ tay Tử Bình — Mậu Thổ sinh tháng Hợi</title>",
                "<title>Tử Bình Đạt Võ — Sổ tay cá nhân</title>");

        html = html.replace("Thổ · mình", "Sức mình")
                .replace("Thủy · tiền", "Tiền & cơ hội")
                .replace("Mộc · sinh Ấn", "Áp lực tốt")
                .replace("Hỏa · dụng thần", "Học & hệ thống")
                .replace("Kim · trống", "Đầu ra còn thiếu")
                .replace("Sau 21h không ký, không chốt, không nhắn tin lúc nóng", "Nếu đã mệt vào cuối ngày, tránh chốt quyết định lớn hoặc nhắn lúc nóng")
                .replace("Ngủ trước 23h", "Giữ giờ ngủ ổn định và đủ giấc")
                .replace("Ăn sáng ấm, đúng giờ. Không bỏ bữa", "Ăn uống đều và phù hợp sức khỏe thực tế")
                .replace("Ra nắng ít nhất mười lăm phút", "Nếu phù hợp sức khỏe, dành thời gian vận động hoặc ra ngoài trời");

        html = html.replace("var v=[\"bình thường\",\"v-mid\"];", "var v=[\"Bình thường\",\"v-mid\"];")
                .replace("if(s>=6){v=[\"rất thuận\",\"v-great\"];}\n", "if(s>=6){v=[\"Ưu tiên cao\",\"v-great\"];}\n")
                .replace("else if(s>=3){v=[\"thuận\",\"v-good\"];}\n", "else if(s>=3){v=[\"Có thể làm\",\"v-good\"];}\n")
                .replace("else if(s<=-4){v=[\"nên lùi\",\"v-low\"];}\n", "else if(s<=-4){v=[\"Hạn chế việc lớn\",\"v-low\"];}\n")
                .replace("else if(s<=-1){v=[\"giữ sức\",\"v-low\"];}\n", "else if(s<=-1){v=[\"Thận trọng\",\"v-low\"];}\n");

        String brandCss = "<style id='datvo-brand'>"
                + ".dv-brand{position:relative;margin:10px 0 18px;padding:18px 14px 16px;text-align:center;overflow:hidden;border:1px solid rgba(240,180,41,.34);border-radius:10px;background:radial-gradient(circle at 50% 0%,rgba(255,150,48,.20),transparent 42%),linear-gradient(180deg,#28160e,#171210 76%);box-shadow:inset 0 0 0 1px rgba(255,205,120,.025),0 12px 34px rgba(0,0,0,.22)}"
                + ".dv-brand:before,.dv-brand:after{content:'';position:absolute;top:50%;width:22%;height:1px;background:linear-gradient(90deg,transparent,#b97d35)}.dv-brand:before{left:0}.dv-brand:after{right:0;transform:scaleX(-1)}"
                + ".dv-seal{display:inline-flex;align-items:center;justify-content:center;width:58px;height:58px;margin-bottom:9px;border:2px solid #e0aa52;border-radius:8px;background:#681d14;color:#f6c76f;font-family:serif;font-weight:800;font-size:22px;line-height:1;letter-spacing:1px;box-shadow:0 0 0 4px rgba(240,180,41,.07),0 7px 18px rgba(0,0,0,.38)}"
                + ".dv-title{font-family:Georgia,'Times New Roman',serif;font-weight:700;font-size:clamp(32px,8vw,50px);line-height:1.08;letter-spacing:.035em;color:#f4c66f;text-shadow:0 1px 0 #6d3a13,0 0 18px rgba(240,180,41,.20);margin:1px 0 7px}"
                + ".dv-title span{color:#fff0c7}.dv-sub{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.19em;text-transform:uppercase;color:#b99569}.dv-rule{display:flex;align-items:center;gap:9px;max-width:360px;margin:10px auto 0;color:#a66d32}.dv-rule i{height:1px;background:linear-gradient(90deg,transparent,#a66d32);flex:1}.dv-rule b{font-family:serif;font-weight:400;color:#d7a34e;font-size:16px}"
                + ".dv-tech{border:1px solid var(--line);border-radius:4px;background:var(--loam-2);margin:10px 0}.dv-tech>summary{padding:10px 12px;cursor:pointer;font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--ash)}.dv-tech .inside{padding:0 12px 12px}.tbl .ts{display:none}"
                + "@media(max-width:640px){.dv-brand{padding:14px 10px 13px;margin:7px 0 14px}.dv-seal{width:50px;height:50px;font-size:19px}.dv-title{font-size:34px}.dv-sub{font-size:9px}.dv-brand:before,.dv-brand:after{width:15%}}"
                + "</style>";
        html = html.replace("</head>", brandCss + "</head>");

        String brand = "<div class='dv-brand' aria-label='Tử Bình Đạt Võ'>"
                + "<div class='dv-seal'>子平</div>"
                + "<div class='dv-title'>Tử Bình <span>Đạt Võ</span></div>"
                + "<div class='dv-sub'>Sổ tay cá nhân · Võ Tấn Đạt</div>"
                + "<div class='dv-rule'><i></i><b>命 · 理</b><i></i></div>"
                + "</div>";
        html = html.replace("<header>", "<header>" + brand);

        String polishScript = "<script>(function(){document.addEventListener('DOMContentLoaded',function(){"
                + "var map={'Rất thuận':'Ưu tiên cao','rất thuận':'Ưu tiên cao','Thuận':'Có thể làm','Nghịch':'Hạn chế việc lớn','Nghịch nặng':'Hạn chế việc lớn','Cần giữ':'Thận trọng','Giữ sức':'Thận trọng'};"
                + "document.querySelectorAll('.pill,.verdict').forEach(function(x){var t=x.textContent.trim();if(map[t])x.textContent=map[t];});"
                + "document.querySelectorAll('.goodhours .lbl').forEach(function(lbl){if(lbl.textContent.toLowerCase().indexOf('thần sát')>=0){var box=lbl.parentElement;var d=document.createElement('details');d.className='dv-tech';var s=document.createElement('summary');s.textContent='Theo sách · dấu hiệu phụ';var inside=document.createElement('div');inside.className='inside';while(box.firstChild)inside.appendChild(box.firstChild);d.appendChild(s);d.appendChild(inside);box.parentNode.replaceChild(d,box);}});"
                + "document.querySelectorAll('td[data-l=\"Vì sao\"]').forEach(function(td){if(td.querySelector('details'))return;var d=document.createElement('details');d.className='dv-tech';var s=document.createElement('summary');s.textContent='Vì sao?';var inside=document.createElement('div');inside.className='inside';while(td.firstChild)inside.appendChild(td.firstChild);d.appendChild(s);d.appendChild(inside);td.appendChild(d);});"
                + "document.querySelectorAll('h3').forEach(function(h){var t=h.textContent.trim();if(t==='Các mối quan hệ trong gia đình'){var n=h.nextElementSibling;while(n&&!n.classList.contains('wrapx'))n=n.nextElementSibling;if(n){var d=document.createElement('details');d.className='dv-tech';var s=document.createElement('summary');s.textContent='Theo sách · lục thân và vị trí';d.appendChild(s);n.parentNode.insertBefore(d,n);d.appendChild(n);}}});"
                + "});})();</script>";
        html = html.replace("</body>", polishScript + "</body>");
        return html;
    }

    private String loadHtml() {
        try {
            StringBuilder encoded = new StringBuilder();
            for (int i = 0; i < 10; i++) {
                String name = String.format("htmlparts/part%02d.txt", i);
                try (InputStream in = getAssets().open(name)) {
                    byte[] buffer = new byte[8192];
                    int n;
                    while ((n = in.read(buffer)) != -1) {
                        encoded.append(new String(buffer, 0, n, StandardCharsets.US_ASCII));
                    }
                }
            }

            byte[] gzip = Base64.decode(encoded.toString(), Base64.DEFAULT);
            try (GZIPInputStream gis = new GZIPInputStream(new ByteArrayInputStream(gzip));
                 ByteArrayOutputStream output = new ByteArrayOutputStream()) {
                byte[] buffer = new byte[8192];
                int n;
                while ((n = gis.read(buffer)) != -1) {
                    output.write(buffer, 0, n);
                }
                return output.toString("UTF-8");
            }
        } catch (Exception e) {
            return "<html><body style='background:#171210;color:white;font-family:sans-serif;padding:24px'>"
                    + "<h2>Không mở được dữ liệu</h2><pre>" + e + "</pre></body></html>";
        }
    }

    @Override
    public void onBackPressed() {
        if (web != null && web.canGoBack()) {
            web.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
