"""AxolOS · textos de las diapositivas del instalador, por idioma (los usa instalador_marca_axolos.py).

Cada idioma es una lista de 5 diapositivas: bienvenida, Axo, búsqueda, programar y actualizaciones.
Los ejemplos de órdenes usan las que entiende AxolOS en ese idioma («ai find …», «axolos-dev install»).
"""
IDIOMAS = ["es", "en", "fr", "ru", "zh_CN", "ja"]

# chino y japonés: mismas fuentes de la marca y, para sus caracteres, Noto CJK de cada idioma
QM_CJK = {"zh_CN": ["Noto Sans CJK SC", "Noto Serif CJK SC"], "ja": ["Noto Sans CJK JP", "Noto Serif CJK JP"]}

TEXTOS = {
    "es": [
        dict(etiqueta="AxolOS", titulo="Te damos la bienvenida",
             cuerpo="CachyOS por debajo, optimizado para tu procesador y tu gráfica. KDE Plasma por encima, "
                    "con el diseño de AxolOS."),
        dict(etiqueta="IA local", titulo="Axo, tu IA en el equipo",
             cuerpo="Pregúntale en su chat o escribe «ia» y tu pregunta en el buscador (Alt+Espacio). "
                    "Funciona sin conexión y conoce tu sistema.",
             pregunta="¿Cómo libero espacio en el disco?",
             respuesta="Mira primero la caché de pacman: «paccache -rk1» deja una versión de cada paquete…",
             privado="Sin internet · nada sale de tu equipo"),
        dict(etiqueta="Búsqueda", titulo="Encuentra cualquier archivo",
             cuerpo="Busca por lo que contienen tus fotos, PDF y documentos, no solo por el nombre. "
                    "Lo nuevo se indexa al momento.",
             consulta="ia busco una foto de la playa", archivos=("playa-agosto.jpg", "atardecer-cadiz.heic"),
             donde=("Imágenes · hace 2 meses", "Descargas · el año pasado", "Cámara · hace 3 años")),
        dict(etiqueta="Para programar", titulo="Listo para tu código",
             cuerpo="Elige tus lenguajes en la Bienvenida y quedan instalados con sus herramientas. Git, terminal "
                    "y editores ya vienen preparados.",
             carpeta="~/proyectos/axo", orden="$ axolos-dev instalar rust python", python="Python · uv y pip",
             commit="Primer commit en AxolOS"),
        dict(etiqueta="Actualizaciones", titulo="Siempre al día",
             cuerpo="Una sola orden actualiza CachyOS y AxolOS. Con Btrfs puedes volver a una instantánea "
                    "anterior desde el menú de arranque.",
             puntos=("sistema y controladores al día", "tema, Bento, Axo y herramientas",
                     "instantánea antes de cada cambio")),
    ],
    "en": [
        dict(etiqueta="AxolOS", titulo="Welcome",
             cuerpo="CachyOS underneath, optimized for your processor and graphics card. KDE Plasma on top, "
                    "with the AxolOS design."),
        dict(etiqueta="Local AI", titulo="Axo, the AI on your computer",
             cuerpo="Ask in its chat, or type «ai» and your question in the search bar (Alt+Space). "
                    "It works offline and knows your system.",
             pregunta="How do I free up disk space?",
             respuesta="Start with the pacman cache: «paccache -rk1» keeps one version of each package…",
             privado="Offline · nothing leaves your computer"),
        dict(etiqueta="Search", titulo="Find any file",
             cuerpo="Search your photos, PDFs and documents by what they contain, not just by name. "
                    "New files are indexed right away.",
             consulta="ai find a photo of the beach", archivos=("beach-august.jpg", "sunset-cadiz.heic"),
             donde=("Pictures · 2 months ago", "Downloads · last year", "Camera · 3 years ago")),
        dict(etiqueta="For developers", titulo="Ready for your code",
             cuerpo="Pick your languages in the Welcome app and they are installed with their tools. Git, the "
                    "terminal and editors come ready to go.",
             carpeta="~/projects/axo", orden="$ axolos-dev install rust python", python="Python · uv and pip",
             commit="First commit on AxolOS"),
        dict(etiqueta="Updates", titulo="Always up to date",
             cuerpo="A single command updates CachyOS and AxolOS. With Btrfs you can go back to an earlier "
                    "snapshot from the boot menu.",
             puntos=("system and drivers up to date", "theme, Bento, Axo and tools", "a snapshot before every change")),
    ],
    "fr": [
        dict(etiqueta="AxolOS", titulo="Bienvenue",
             cuerpo="CachyOS en dessous, optimisé pour votre processeur et votre carte graphique. KDE Plasma "
                    "au-dessus, avec le design d'AxolOS."),
        dict(etiqueta="IA locale", titulo="Axo, l'IA de votre ordinateur",
             cuerpo="Posez vos questions dans son chat ou tapez « ai » suivi de votre question dans la recherche "
                    "(Alt+Espace). Il fonctionne hors ligne et connaît votre système.",
             pregunta="Comment libérer de l'espace ?",
             respuesta="Commencez par le cache de pacman : « paccache -rk1 » garde une version de chaque paquet…",
             privado="Hors ligne · rien ne sort de votre ordinateur"),
        dict(etiqueta="Recherche", titulo="Trouvez n'importe quel fichier",
             cuerpo="Cherchez dans vos photos, PDF et documents selon leur contenu, pas seulement leur nom. "
                    "Les nouveautés sont indexées aussitôt.",
             consulta="ai cherche une photo de la plage", archivos=("plage-aout.jpg", "coucher-soleil-cadix.heic"),
             donde=("Images · il y a 2 mois", "Téléchargements · l'an dernier", "Appareil photo · il y a 3 ans")),
        dict(etiqueta="Pour développer", titulo="Prêt pour votre code",
             cuerpo="Choisissez vos langages dans l'accueil et ils s'installent avec leurs outils. Git, le "
                    "terminal et les éditeurs sont déjà prêts.",
             carpeta="~/projets/axo", orden="$ axolos-dev install rust python", python="Python · uv et pip",
             commit="Premier commit sur AxolOS"),
        dict(etiqueta="Mises à jour", titulo="Toujours à jour",
             cuerpo="Une seule commande met à jour CachyOS et AxolOS. Avec Btrfs, vous pouvez revenir à un "
                    "instantané précédent depuis le menu de démarrage.",
             puntos=("système et pilotes à jour", "thème, Bento, Axo et outils", "un instantané avant chaque changement")),
    ],
    "ru": [
        dict(etiqueta="AxolOS", titulo="Добро пожаловать",
             cuerpo="Внутри — CachyOS, оптимизированный под ваш процессор и видеокарту. Сверху — KDE Plasma "
                    "в оформлении AxolOS."),
        dict(etiqueta="Локальный ИИ", titulo="Axo — ИИ на вашем компьютере",
             cuerpo="Спросите в чате или введите «ии» и вопрос в поиске (Alt+Пробел). Работает без интернета "
                    "и знает вашу систему.",
             pregunta="Как освободить место на диске?",
             respuesta="Начните с кэша pacman: «paccache -rk1» оставит по одной версии каждого пакета…",
             privado="Без интернета · ничего не покидает компьютер"),
        dict(etiqueta="Поиск", titulo="Найдите любой файл",
             cuerpo="Ищите фото, PDF и документы по содержимому, а не только по имени. Новые файлы "
                    "индексируются сразу.",
             consulta="ии найди фото пляжа", archivos=("plyazh-avgust.jpg", "zakat-kadis.heic"),
             donde=("Изображения · 2 месяца назад", "Загрузки · в прошлом году", "Камера · 3 года назад")),
        dict(etiqueta="Для разработчиков", titulo="Готов к вашему коду",
             cuerpo="Выберите языки в\u00a0приветствии — они установятся вместе с инструментами. Git, терминал "
                    "и редакторы уже настроены.",
             carpeta="~/projects/axo", orden="$ axolos-dev install rust python", python="Python · uv и pip",
             commit="Первый коммит в AxolOS"),
        dict(etiqueta="Обновления", titulo="Всегда актуально",
             cuerpo="Одна команда обновляет CachyOS и AxolOS. С\u00a0Btrfs можно вернуться к прежнему снимку "
                    "из меню загрузки.",
             puntos=("система и драйверы всегда свежие", "тема, Bento, Axo и инструменты", "снимок перед каждым изменением")),
    ],
    "zh_CN": [
        dict(etiqueta="AxolOS", titulo="欢迎",
             cuerpo="底层是 CachyOS，针对你的处理器和显卡优化；上层是 KDE Plasma，采用 AxolOS 的设计。"),
        dict(etiqueta="本地 AI", titulo="Axo，你电脑里的 AI",
             cuerpo="在聊天窗口中提问，或在搜索栏（Alt+空格）输入“ai”加上你的问题。无需联网，而且了解你的系统。",
             pregunta="怎么释放磁盘空间？",
             respuesta="先看看 pacman 缓存：“paccache -rk1”会让每个软件包只保留一个版本…",
             privado="无需联网 · 数据不出本机"),
        dict(etiqueta="搜索", titulo="找到任何文件",
             cuerpo="按内容搜索照片、PDF 和文档，而不只是文件名。新文件会立即建立索引。",
             consulta="ai 找一下海滩的照片", archivos=("海滩-八月.jpg", "加的斯日落.heic"),
             donde=("图片 · 2 个月前", "下载 · 去年", "相机 · 3 年前")),
        dict(etiqueta="为开发者", titulo="为你的代码做好准备",
             cuerpo="在欢迎程序中选择编程语言，即可连同工具一起安装。Git、终端和编辑器都已准备就绪。",
             carpeta="~/projects/axo", orden="$ axolos-dev install rust python", python="Python · uv 和 pip",
             commit="在 AxolOS 上的第一次提交"),
        dict(etiqueta="更新", titulo="始终保持最新",
             cuerpo="一条命令即可更新 CachyOS 和 AxolOS。借助 Btrfs，你可以在启动菜单中回到之前的快照。",
             puntos=("系统和驱动保持最新", "主题、Bento、Axo 和工具", "每次更改前自动快照")),
    ],
    "ja": [
        dict(etiqueta="AxolOS", titulo="ようこそ",
             cuerpo="土台は CachyOS。プロセッサーとグラフィックスに合わせて最適化されています。その上に、"
                    "AxolOS デザインの KDE Plasma。"),
        dict(etiqueta="ローカル AI", titulo="Axo、手元の AI",
             cuerpo="チャットで質問するか、検索（Alt+Space）で「ai」に続けて質問を入力。オフラインで動き、"
                    "システムのことも分かります。",
             pregunta="ディスクの空きを増やすには？",
             respuesta="まず pacman のキャッシュを確認：「paccache -rk1」で各パッケージを 1 世代だけ残せます…",
             privado="オフライン · データは外に出ません"),
        dict(etiqueta="検索", titulo="何でもすぐ見つかる",
             cuerpo="写真や PDF、文書を名前だけでなく中身で検索。新しいファイルはすぐにインデックスされます。",
             consulta="ai 探して 海の写真", archivos=("海-8月.jpg", "カディスの夕日.heic"),
             donde=("ピクチャ · 2 か月前", "ダウンロード · 昨年", "カメラ · 3 年前")),
        dict(etiqueta="開発者向け", titulo="コードの準備は万全",
             cuerpo="ようこそ画面で言語を選ぶだけで、ツールと一緒にインストール。Git、ターミナル、"
                    "エディターも準備済みです。",
             carpeta="~/projects/axo", orden="$ axolos-dev install rust python", python="Python · uv と pip",
             commit="AxolOS での最初のコミット"),
        dict(etiqueta="アップデート", titulo="いつも最新",
             cuerpo="コマンド 1 つで CachyOS と AxolOS を更新。Btrfs なので、起動メニューから以前の"
                    "スナップショットに戻せます。",
             puntos=("システムとドライバーを最新に", "テーマ、Bento、Axo、ツール", "変更のたびにスナップショット")),
    ],
}


def _tipografia_fr(v):
    """Francés: espacio no separable dentro de « » y antes de : ? ! (que no se partan de línea)."""
    if isinstance(v, str):
        for a, b in (("« ", "«\u00a0"), (" »", "\u00a0»"), (" :", "\u00a0:"), (" ?", "\u00a0?"), (" !", "\u00a0!")):
            v = v.replace(a, b)
        return v
    return tuple(_tipografia_fr(x) for x in v)


TEXTOS["fr"] = [{k: _tipografia_fr(v) for k, v in d.items()} for d in TEXTOS["fr"]]
