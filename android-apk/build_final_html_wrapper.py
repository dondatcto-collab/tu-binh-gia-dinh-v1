import build_final_html as app

original = app.transform
app.transform = lambda html: original(html).replace('tỉnh tááo', 'tỉnh táo')
app.main()
