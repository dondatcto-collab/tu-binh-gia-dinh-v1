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
        web.loadDataWithBaseURL("https://local.tubinh.vn/", loadHtml(), "text/html", "UTF-8", null);
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
