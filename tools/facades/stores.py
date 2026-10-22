"""Especificacao de cada loja/restaurante: (casas, andares, spec). Textos sempre em ingles."""

F = "food"

STORES = {
    # ------------------------------------------------------------ restaurantes nivel 1 (4 casas)
    "restaurant-level-one-a": (4, 1, dict(
        kind=F, title="Cafe & Bakery", font="fancy", sign="board", sign_bg=(70, 44, 34), ink=(240, 220, 180),
        wall="brick", wall_color=(150, 84, 66), front="wood", frame=(60, 40, 30), door="right", door_w=70,
        awning=[(140, 40, 40), (230, 220, 200)], interior="counter", counter_items=["bread", "cake", "bread"],
        back_items=["bread"], closed="easel", menu_title="BAKED DAILY")),
    "restaurant-level-one-b": (4, 1, dict(
        kind=F, title="TAKE-OUT", font="impact", sign="board", sign_bg=(200, 60, 40), ink=(255, 240, 200),
        wall="tiles", wall_color=(200, 200, 190), front="modern", frame=(40, 40, 44), door="left", door_w=66,
        interior="counter", counter_items=["burger", "cup", "box"], closed="grille_door", menu_title="TO GO")),
    "restaurant-level-one-c": (4, 1, dict(
        kind=F, title="Lunch Box", font="cooper", sign="letters", ink=(240, 200, 80),
        wall="planks", wall_color=(90, 120, 110), front="modern", frame=(30, 40, 40), door="right", door_w=66,
        interior="counter", counter_items=["sandwich", "box", "can"], back_items=["can", "box"], closed="placard",
        closed_lines=("SOLD OUT", "CLOSED"))),
    "restaurant-level-one-d": (4, 1, dict(
        kind=F, title="Café", font="calligraphy", sign="oval", sign_bg=(30, 50, 44), ink=(230, 210, 160),
        sign_trim=(190, 160, 90), wall="stucco", wall_color=(196, 170, 130), front="arch", frame=(40, 50, 46),
        door="left", door_w=66, interior="tables", menu_board=False, decor=["mirror", "frame", "plant"],
        closed="hanging", extras=["pots"])),
    "restaurant-level-one-e": (4, 1, dict(
        kind=F, title="SANDWICHES", font="slab", sign="board", sign_bg=(240, 220, 160), ink=(60, 40, 30),
        sign_trim=(60, 40, 30), wall="brick", wall_color=(110, 70, 56), front="modern", frame=(50, 40, 34),
        door="right", door_w=66, awning=[(40, 110, 60), (240, 230, 210)], interior="counter",
        counter_items=["sandwich"], closed="neon", neon_color=(220, 60, 60))),
    "restaurant-level-one-g": (4, 1, dict(
        kind=F, title="Ice Cream", font="jokerman", sign="board", sign_bg=(250, 200, 220), ink=(180, 40, 110),
        sign_trim=(255, 255, 255), wall="stripes", wall_color=(240, 200, 215), wall_color2=(250, 245, 240),
        front="modern", frame=(200, 120, 160), door="left", door_w=62, interior="counter",
        counter_items=["ice_tubs", "ice_cream"], back_items=["ice_cream"], closed="hanging",
        closed_plate=(180, 40, 110), menu_title="FLAVORS")),
    "restaurant-level-one-h": (4, 1, dict(
        kind=F, title="Smoothie Bar", font="harlow", sign="neon", ink=(120, 230, 120), wall="tiles",
        wall_color=(110, 190, 150), front="modern", frame=(30, 60, 50), door="right", door_w=62, interior="counter",
        counter_items=["smoothie", "fruit_crate"], back_items=["smoothie"], closed="placard",
        closed_lines=("BACK", "TOMORROW"))),
    "restuarant-level-one-f": (4, 1, dict(
        kind=F, title="DONUTS", font="ravie", sign="marquee", sign_bg=(240, 150, 180), ink=(120, 50, 30),
        wall="tiles", wall_color=(250, 230, 200), front="modern", frame=(150, 80, 60), door="left", door_w=62,
        awning=[(240, 120, 160), (255, 245, 240)], interior="counter", counter_items=["donut"],
        back_items=["donut"], closed="grille_door")),

    # ------------------------------------------------------------ varejo nivel 1 (7 casas)
    "retail-level-one-a": (7, 1, dict(
        title="24/7 MART", subtitle="CONVENIENCE STORE", font="impact", sign="board", sign_bg=(30, 110, 60),
        ink=(255, 255, 255), wall="panels", wall_color=(170, 175, 180), front="modern", frame=(40, 44, 50),
        door="right", items=["can", "box", "bottle", "grocery"], shelves=3, closed="grille",
        closed_text="CLOSED")),
    "retail-level-one-b": (7, 1, dict(
        title="Mobile World", font="bauhaus", sign="letters", ink=(120, 200, 255), wall="panels",
        wall_color=(60, 66, 80), front="modern", frame=(30, 32, 40), door="center", items=["phone", "laptop", "console"],
        shelves=2, closed="neon", neon_color=(80, 160, 255))),
    "retail-level-one-c": (7, 1, dict(
        title="NEWS & MAGAZINES", font="condensed", sign="board", sign_bg=(30, 30, 34), ink=(240, 200, 60),
        wall="brick", wall_color=(120, 70, 50), front="wood", frame=(40, 60, 46), door="left",
        items=["newspaper", "magazine", "magazine"], shelves=3, awning=[(40, 60, 46)], awning_text="DAILY PAPERS",
        closed="shutter_half", shutter_drop=0.55)),
    "retail-level-one-d": (7, 1, dict(
        title="PHARMACY", font="sans", sign="board", sign_bg=(240, 244, 240), ink=(30, 130, 70), sign_trim=(30, 130, 70),
        wall="tiles", wall_color=(220, 225, 226), front="modern", frame=(70, 80, 84), door="center",
        items=["pills", "cosmetics", "pills", "box"], shelves=3, closed="placard",
        closed_lines=("PHARMACY", "CLOSED"), extras=["flag"], flag=(30, 160, 80))),
    "retail-level-one-e-bottle": (7, 1, dict(
        title="Wine & Spirits", font="elegant", sign="board", sign_bg=(80, 24, 34), ink=(230, 200, 140),
        sign_trim=(200, 170, 110), wall="stone", wall_color=(140, 128, 110), front="classic", frame=(60, 30, 34),
        door="left", items=["bottle"], shelves=3, door_color=(70, 30, 34), closed="hanging",
        closed_plate=(80, 24, 34), closed_ink=(230, 200, 140))),
    "retail-level-one-e-flowers": (7, 1, dict(
        title="Flower Store", font="script", sign="board", sign_bg=(40, 62, 54), ink=(226, 222, 206),
        wall="stucco", wall_color=(170, 190, 180), front="wood", frame=(40, 62, 54), door="center",
        items=["flower", "pot_plant", "flower"], shelves=2, awning=[(60, 110, 80), (240, 236, 220)],
        closed="hanging", extras=["planters"])),
    "retail-level-one-f": (7, 1, dict(
        title="SUNGLASS HUT", font="gill", sign="letters", ink=(250, 210, 80), wall="marble",
        wall_color=(220, 214, 200), front="modern", frame=(150, 120, 60), door="right", items=["sunglasses"],
        shelves=3, closed="neon", neon_color=(250, 160, 60))),
    "retail-level-one-g": (7, 1, dict(
        title="Vinyl Records", font="broadway", sign="marquee", sign_bg=(30, 20, 40), ink=(240, 120, 200),
        wall="brick", wall_color=(70, 60, 80), front="modern", frame=(20, 20, 26), door="left", items=["record"],
        shelves=2, window_text="NEW ARRIVALS", window_font="comic", closed="grille", extras=["bike"])),
    "retail-level-one-h": (7, 1, dict(
        title="Shades", subtitle="SUNGLASSES & EYEWEAR", font="magneto", sign="board", sign_bg=(20, 60, 90),
        ink=(250, 250, 255), wall="planks", wall_color=(200, 190, 170), front="modern", frame=(20, 60, 90),
        door="center", items=["sunglasses"], shelves=2, awning=[(20, 60, 90), (240, 240, 240)],
        closed="placard", closed_lines=("SORRY", "WE'RE CLOSED"))),
    "retail-level-one-i": (7, 1, dict(
        title="Happy Paws", subtitle="PET SUPPLIES", font="comic", sign="board", sign_bg=(250, 190, 60),
        ink=(90, 50, 20), wall="stucco", wall_color=(120, 160, 190), front="wood", frame=(90, 60, 30), door="left",
        items=["fishtank", "pet_bed", "box"], display="floor", awning=[(240, 120, 40), (250, 220, 120)],
        closed="easel", closed_lines=("CLOSED", "pets are", "sleeping"))),
    "retail-level-one-j": (7, 1, dict(
        title="Watch & Jewelry Repair", font="bodoni", sign="board", sign_bg=(20, 20, 24), ink=(220, 190, 120),
        sign_trim=(220, 190, 120), wall="marble", wall_color=(80, 80, 86), front="classic", frame=(30, 30, 34),
        door="right", items=["watch", "jewelry"], shelves=2, closed="grille_door")),

    # ------------------------------------------------------------ restaurantes nivel 2 (8 casas)
    "restaurant-level-two-a": (8, 1, dict(
        kind=F, title="BURGER RUSH", font="impact", sign="board", sign_bg=(230, 60, 40), ink=(255, 220, 60),
        sign_trim=(255, 220, 60), wall="tiles", wall_color=(240, 200, 60), front="modern", frame=(180, 40, 30),
        door="right", interior="tables_counter", counter_items=["burger", "cup", "box"], closed="neon",
        menu_title="COMBO MEALS")),
    "restaurant-level-two-b": (8, 1, dict(
        kind=F, title="The Deli Counter", font="serif", sign="board", sign_bg=(30, 40, 60), ink=(240, 230, 200),
        wall="brick", wall_color=(140, 90, 70), front="wood", frame=(30, 40, 60), door="left",
        awning=[(30, 40, 60), (240, 230, 200)], interior="tables_counter", counter_items=["sandwich", "cheese"],
        back_items=["bottle", "can"], closed="hanging")),
    "restaurant-level-two-c": (8, 1, dict(
        kind=F, title="HOT BAR", subtitle="BUFFET BY THE POUND", font="condensed", sign="board",
        sign_bg=(200, 90, 30), ink=(255, 250, 230), wall="tiles", wall_color=(180, 80, 50), front="modern",
        frame=(50, 30, 24), door="center", interior="counter", counter_items=["pizza", "bread", "cup"],
        closed="grille")),
    "restaurant-level-two-d": (8, 1, dict(
        kind=F, title="Diner", font="forte", sign="neon", ink=(80, 220, 240), back_items=["cake", "cup"], wall="panels",
        wall_color=(190, 196, 204), front="modern", frame=(150, 156, 166), door="left", interior="booths",
        accent=(190, 40, 50), closed="placard", closed_lines=("CLOSED", "OPEN 6AM"), menu_title="BLUE PLATE")),
    "restaurant-level-two-e": (8, 1, dict(
        kind=F, title="Pizzeria Napoli", font="brush", sign="board", sign_bg=(240, 236, 220), ink=(170, 40, 40),
        sign_trim=(40, 120, 60), wall="brick", wall_color=(170, 100, 70), front="arch", frame=(40, 80, 50),
        door="right", awning=[(40, 120, 60), (240, 236, 220), (190, 40, 40)], interior="tables_counter",
        counter_items=["pizza"], back_items=["bottle"], closed="easel",
        closed_lines=("CLOSED", "see you", "tomorrow"))),
    "restaurant-level-two-g": (8, 1, dict(
        kind=F, title="The Red Lion", subtitle="PUBLIC HOUSE", font="gothic", sign="board", sign_bg=(30, 50, 34),
        ink=(230, 200, 120), sign_trim=(200, 170, 100), wall="planks", wall_color=(40, 60, 44), front="wood",
        frame=(30, 46, 32), door="center", door_color=(30, 46, 32), interior="bar",
        counter_items=["beer_taps", "pint"], back_items=["bottle"], accent=(110, 40, 30), closed="hanging",
        closed_text="LAST ORDERS", extras=["sconces"])),
    "restaurant-level-two-h": (8, 1, dict(
        kind=F, title="BERLIN CAFE", subtitle="POETRY & COFFEE", font="stencil", sign="letters", ink=(250, 90, 70),
        wall="stucco", wall_color=(70, 70, 72), front="modern", frame=(20, 20, 22), door="left",
        interior="tables_counter", counter_items=["coffee_machine", "books"], back_items=["books"],
        closed="shutter_half", shutter_drop=0.35, closed_text="CLOSED")),

    # ------------------------------------------------------------ varejo nivel 4 (8 casas)
    "retail-level-four-a": (8, 1, dict(
        title="Fine China", font="elegant", sign="board", sign_bg=(30, 50, 100), ink=(240, 240, 250),
        sign_trim=(200, 200, 210), wall="marble", wall_color=(220, 222, 230), front="classic", frame=(30, 50, 100),
        door="center", items=["china"], shelves=2, closed="hanging", closed_plate=(30, 50, 100))),
    "retail-level-four-b": (8, 1, dict(
        title="Belle Cosmetics", font="vivaldi", sign="letters", ink=(255, 205, 220), font_size=44, wall="marble",
        wall_color=(60, 40, 50), front="modern", frame=(200, 160, 120), door="right", items=["cosmetics", "soap"],
        shelves=3, closed="placard", closed_lines=("CLOSED",))),
    "retail-level-four-c": (8, 1, dict(
        title="Goldsmith & Co.", font="bodoni", sign="board", sign_bg=(20, 20, 24), ink=(230, 200, 120),
        sign_trim=(230, 200, 120), wall="stone", wall_color=(110, 106, 100), front="classic", frame=(20, 20, 24),
        door="left", items=["jewelry", "watch"], shelves=2, closed="grille", extras=["sconces"])),
    "retail-level-four-d": (8, 1, dict(
        title="DIAMONDS", subtitle="FINE JEWELERS", font="algerian", sign="board", sign_bg=(70, 20, 40),
        ink=(240, 230, 250), wall="marble", wall_color=(230, 226, 220), front="arch", frame=(70, 20, 40),
        door="center", items=["jewelry"], shelves=1, closed="grille_door")),
    "retail-level-four-e": (8, 1, dict(
        title="Antiquarian Books", font="calligraphy", sign="board", sign_bg=(60, 34, 24), ink=(230, 210, 160),
        wall="planks", wall_color=(90, 60, 40), front="wood", frame=(60, 34, 24), door="right",
        door_color=(60, 34, 24), items=["books"], shelves=3, closed="hanging", closed_text="CLOSED",
        extras=["lamps"])),
    "retail-level-four-f": (8, 1, dict(
        title="Vintners", subtitle="FINE WINE BROKERS", font="elegant", sign="oval", sign_bg=(90, 20, 40),
        ink=(240, 220, 170), wall="stone", wall_color=(150, 120, 100), front="arch", frame=(60, 30, 30),
        door="left", items=["bottle", "wine_glass"], shelves=2, closed="placard",
        closed_lines=("BY", "APPOINTMENT"))),
    "retail-level-four-g": (8, 1, dict(
        title="Wick & Lather", subtitle="CANDLES & SOAP", font="papyrus", sign="board", sign_bg=(220, 210, 180),
        ink=(90, 70, 50), sign_trim=(120, 100, 70), wall="stucco", wall_color=(200, 180, 190), front="wood",
        frame=(120, 100, 80), door="center", items=["candle", "soap", "candle"], shelves=2,
        awning=[(150, 120, 140), (240, 230, 220)], closed="easel", closed_lines=("CLOSED", "light a", "candle!"))),

    # ------------------------------------------------------------ 12 casas
    # (os terracos restaurant-roof-* nao tem imagem: sao transparentes, o mod so escurece o desenho deles)
    "retail-level-two-a": (12, 1, dict(
        title="THREADS", subtitle="CLOTHING", font="gill", sign="letters", ink=(250, 250, 250), wall="panels",
        wall_color=(50, 54, 60), front="modern", frame=(20, 20, 24), door="center", items=["clothes_rack", "mannequin"],
        display="racks", closed="placard", closed_lines=("CLOSED",))),
    "retail-level-two-b": (12, 1, dict(
        title="ELECTRO", subtitle="TV  AUDIO  COMPUTERS", font="bauhaus", sign="board", sign_bg=(20, 40, 90),
        ink=(250, 210, 40), wall="panels", wall_color=(140, 146, 156), front="modern", frame=(30, 34, 44),
        door="right", items=["tv", "laptop", "console"], shelves=2, closed="grille")),
    "retail-level-two-c-purses": (12, 1, dict(
        title="Bags & Briefcases", font="bodoni", sign="board", sign_bg=(110, 60, 30), ink=(245, 230, 200),
        wall="stucco", wall_color=(200, 180, 150), front="classic", frame=(80, 44, 24), door="left",
        items=["purse", "briefcase"], shelves=2, awning=[(110, 60, 30)], closed="hanging")),
    "retail-level-two-c-shoes": (12, 1, dict(
        title="Step Up Shoes", font="slab", sign="board", sign_bg=(30, 30, 34), ink=(240, 120, 60),
        wall="brick", wall_color=(90, 90, 96), front="modern", frame=(30, 30, 34), door="center",
        items=["shoe", "sport_shoe"], shelves=3, closed="shutter_half", shutter_drop=0.3)),
    "retail-level-two-d": (12, 1, dict(
        title="Home Goods", subtitle="HOUSEWARES & KITCHEN", font="round", sign="board", sign_bg=(240, 240, 236),
        ink=(40, 90, 140), sign_trim=(40, 90, 140), wall="planks", wall_color=(170, 190, 200), front="wood",
        frame=(40, 90, 140), door="right", items=["china", "box", "floor_lamp", "pot_plant"], shelves=2,
        closed="neon", neon_color=(240, 90, 80))),
    "retail-level-two-e": (12, 1, dict(
        title="The Cheese Cellar", subtitle="ARTISAN CHEESE", font="calligraphy", sign="board", sign_bg=(240, 220, 150),
        ink=(90, 60, 20), sign_trim=(90, 60, 20), wall="stone", wall_color=(170, 150, 120), front="wood",
        frame=(90, 70, 40), door="left", door_color=(90, 70, 40), items=["cheese"], shelves=3,
        awning=[(200, 160, 50), (250, 240, 210)], closed="easel", closed_lines=("CLOSED", "back", "tomorrow"))),
    "retail-level-two-f": (12, 1, dict(
        title="Sweet Tooth", subtitle="CANDY STORE", font="jokerman", sign="marquee", sign_bg=(250, 220, 240),
        ink=(200, 40, 120), wall="stripes", wall_color=(250, 200, 220), wall_color2=(250, 250, 245), front="modern",
        frame=(200, 40, 120), door="center", items=["candy_jar", "lollipop"], shelves=2,
        awning=[(200, 40, 120), (250, 250, 245)], closed="hanging", closed_plate=(200, 40, 120))),
    "retail-level-two-g": (12, 1, dict(
        title="SURF & SWIM", subtitle="SWIMWEAR OUTLET", font="showcard", sign="board", sign_bg=(30, 150, 190),
        ink=(255, 240, 120), wall="planks", wall_color=(80, 170, 190), front="modern", frame=(250, 200, 80),
        door="left", items=["swimsuit", "beach_ball", "sunglasses"], shelves=2,
        awning=[(250, 200, 80), (30, 150, 190)], closed="placard", closed_lines=("GONE", "SURFING"))),
    "retail-level-two-h": (12, 1, dict(
        title="Glamour Salon", subtitle="HAIR  NAILS  BEAUTY", font="fancy", sign="letters", ink=(255, 220, 235), font_size=42,
        wall="marble", wall_color=(70, 50, 70), front="modern", frame=(200, 170, 120), door="right",
        items=["salon_chair"], display="floor", closed="neon", neon_color=(240, 100, 180), extras=["pots"])),
    "retail-level-two-i": (12, 1, dict(
        title="ANARCHY", subtitle="COUNTERCULTURE CLOTHING", font="chiller", sign="board", sign_bg=(20, 20, 20),
        ink=(220, 40, 40), font_size=40, wall="brick", wall_color=(50, 46, 50), front="modern", frame=(20, 20, 20),
        door="left", items=["tshirt_band", "skull_rack", "record"], shelves=2, closed="grille")),
    "retail-level-two-j": (12, 1, dict(
        title="CITY SAVINGS BANK", font="serif", sign="letters", ink=(250, 235, 180), font_size=36, wall="stone",
        wall_color=(160, 156, 150), front="classic", frame=(40, 44, 54), door="center", door_w=140,
        items=["atm", "pot_plant"], display="floor", closed="placard", closed_lines=("BANK", "CLOSED"),
        window_text="Open Mon - Fri  9 - 5", window_font="serif", extras=["flag"], flag=(40, 60, 140))),

    # ------------------------------------------------------------ restaurantes nivel 4 (14 casas)
    "restaurant-level-four-a": (14, 1, dict(
        kind=F, title="Golden Dragon", font="papyrus", sign="board", sign_bg=(160, 20, 20), ink=(250, 210, 80),
        sign_trim=(250, 200, 60), wall="tiles", wall_color=(120, 30, 30), front="classic", frame=(110, 20, 20),
        door="center", interior="tables", wood=(90, 30, 20), tablecloth=(230, 225, 215), decor=["lantern", "frame"], closed="hanging", closed_plate=(160, 20, 20),
        closed_ink=(250, 210, 80), extras=["lanterns"], menu_title="DIM SUM")),
    "restaurant-level-four-b": (14, 1, dict(
        kind=F, title="Taj Mahal", subtitle="INDIAN CUISINE", font="harlow", sign="board", sign_bg=(240, 150, 40),
        ink=(110, 20, 60), sign_trim=(110, 20, 60), wall="stucco", wall_color=(200, 120, 70), front="arch",
        frame=(110, 20, 60), door="left", interior="tables", wood=(120, 60, 40), tablecloth=(240, 200, 90), decor=["frame", "mirror", "plant"], closed="placard",
        closed_lines=("CLOSED", "OPEN 5PM"), extras=["lanterns"], lantern_color=(240, 150, 40))),
    "restaurant-level-four-c": (14, 1, dict(
        kind=F, title="The Oyster House", font="elephant", sign="board", sign_bg=(30, 60, 90), ink=(240, 240, 230),
        sign_trim=(200, 180, 120), wall="planks", wall_color=(60, 110, 140), front="wood", frame=(240, 240, 230),
        door="right", awning=[(30, 60, 90), (240, 240, 230)], interior="tables_counter",
        counter_items=["wine_glass", "plate_set"], tablecloth=(235, 235, 240), decor=["frame", "clock", "shelf"], closed="easel", closed_lines=("CLOSED", "fresh catch", "tomorrow"))),
    "restaurant-level-four-d": (14, 1, dict(
        kind=F, title="Thai Orchid", font="script", sign="board", sign_bg=(80, 30, 100), ink=(250, 210, 120),
        wall="planks", wall_color=(70, 40, 60), front="modern", frame=(150, 110, 40), door="center",
        interior="tables", wood=(80, 50, 30), tablecloth=(150, 60, 140), decor=["plant", "frame"], closed="neon", neon_color=(250, 120, 200), extras=["pots", "lanterns"],
        lantern_color=(240, 180, 60))),
    "restaurant-level-four-e": (14, 1, dict(
        kind=F, title="SAKURA", subtitle="SUSHI  ·  JAPANESE", font="brush", sign="board", sign_bg=(240, 236, 226),
        ink=(30, 30, 30), sign_trim=(30, 30, 30), wall="planks", wall_color=(120, 90, 60), front="modern",
        frame=(40, 30, 24), door="left", interior="bar", counter_items=["sushi"], accent=(40, 30, 24),
        closed="hanging", closed_plate=(240, 236, 226), closed_ink=(160, 30, 30), extras=["lanterns"],
        lantern_color=(230, 230, 220))),
    "restaurant-level-four-f": (14, 1, dict(
        kind=F, title="Le Petit Bistro", font="fancy", sign="board", sign_bg=(20, 40, 70), ink=(240, 220, 170),
        sign_trim=(200, 170, 100), wall="stone", wall_color=(200, 190, 170), front="classic", frame=(20, 40, 70),
        door="center", awning=[(160, 30, 40)], awning_text="FRENCH CUISINE", interior="tables", tablecloth=(240, 240, 236), decor=["mirror", "frame", "shelf"],
        counter_items=["plate_set"], closed="easel", closed_lines=("CLOSED", "see you", "tomorrow"))),
    "restaurant-level-four-g": (14, 1, dict(
        kind=F, title="The Velvet Lounge", font="vivaldi", sign="neon", ink=(200, 120, 240), wall="marble",
        wall_color=(40, 30, 40), front="modern", frame=(150, 120, 60), door="right", interior="bar",
        counter_items=["cocktail", "wine_glass"], back_items=["bottle"], accent=(110, 30, 70), closed="placard",
        closed_lines=("CLOSED", "OPEN 6PM"), blinds=0.25)),

    # ------------------------------------------------------------ outros tamanhos
    "restaurant-level-two-f": (8, 1, dict(
        kind=F, title="MIDNIGHT DINER", subtitle="ALWAYS FRESH COFFEE", font="broadway", sign="marquee",
        sign_bg=(30, 30, 40), ink=(250, 200, 60), wall="tiles", wall_color=(170, 40, 40), front="modern",
        frame=(200, 200, 205), door="center", interior="booths", accent=(40, 120, 160),
        closed="placard", closed_lines=("SORRY", "CLOSED FOR", "CLEANING"))),

    # ------------------------------------------------------------ restaurantes nivel 3 (16 casas)
    "restaurant-level-three-a": (16, 1, dict(
        kind=F, title="THE END ZONE", subtitle="SPORTS BAR & GRILL", font="impact", sign="neon", ink=(250, 140, 40),
        wall="panels", wall_color=(46, 50, 60), front="modern", frame=(200, 40, 40), door="right", door_w=110,
        interior="bar", counter_items=["beer_taps", "pint", "burger"], accent=(200, 40, 40), decor=["tv"],
        closed="shutter_half", shutter_drop=0.3, extras=["flag"], flag=(200, 40, 40), menu_title="GAME DAY")),
    "restaurant-level-three-b-italian": (16, 1, dict(
        kind=F, title="Trattoria Bella", font="script", sign="board", sign_bg=(30, 70, 40), ink=(250, 240, 220),
        sign_trim=(190, 40, 40), wall="stucco", wall_color=(210, 160, 110), front="arch", frame=(30, 70, 40),
        door="center", door_w=110, awning=[(30, 110, 50), (245, 240, 230), (190, 40, 40)], interior="tables",
        tablecloth=(200, 60, 60), decor=["frame", "shelf", "plant"], shelf_items=["bottle", "bread"],
        closed="hanging", extras=["pots"])),
    "restaurant-level-three-b-mexican": (16, 1, dict(
        kind=F, title="Casa Fiesta", subtitle="MEXICAN GRILL", font="showcard", sign="board", sign_bg=(240, 180, 40),
        ink=(160, 30, 60), sign_trim=(40, 140, 120), wall="tiles", wall_color=(220, 120, 60), front="arch",
        frame=(40, 110, 100), door="left", door_w=110, interior="tables_counter", counter_items=["bottle", "cup"],
        tablecloth=(60, 170, 150), decor=["pennant"], closed="easel", closed_lines=("CLOSED", "adios", "amigos!"),
        extras=["pots"])),
    "restaurant-level-three-c-brunch": (16, 1, dict(
        kind=F, title="Sunny Side Up", subtitle="BREAKFAST & BRUNCH", font="forte", sign="board",
        sign_bg=(250, 220, 90), ink=(200, 90, 30), sign_trim=(255, 255, 255), wall="stripes",
        wall_color=(250, 230, 160), wall_color2=(255, 250, 235), front="wood", frame=(90, 140, 170), door="right",
        door_w=110, awning=[(90, 140, 170), (255, 250, 235)], interior="tables_counter",
        counter_items=["coffee_machine", "cake", "bread"], decor=["clock", "plant", "frame"], closed="placard",
        closed_lines=("CLOSED", "OPEN 6AM"))),
    "restaurant-level-three-c-family": (16, 1, dict(
        kind=F, title="Grandma's Kitchen", subtitle="FAMILY RESTAURANT", font="cooper", sign="board",
        sign_bg=(130, 40, 40), ink=(250, 235, 200), wall="brick", wall_color=(170, 110, 80), front="wood",
        frame=(90, 60, 40), door="center", door_w=110, door_color=(90, 60, 40), interior="booths",
        accent=(60, 110, 150), back_items=["cake", "pot_plant", "cup"], decor=["frame", "clock"], closed="neon",
        neon_color=(240, 80, 70), extras=["planters"])),
    "restaurant-level-three-d": (16, 1, dict(
        kind=F, title="GOLDEN BUFFET", subtitle="ALL YOU CAN EAT", font="broadway", sign="marquee",
        sign_bg=(120, 20, 20), ink=(250, 210, 80), wall="marble", wall_color=(150, 40, 40), front="classic",
        frame=(200, 160, 60), door="sides", door_w=100, interior="counter",
        counter_items=["pizza", "bread", "sandwich", "cake", "ice_tubs"], closed="grille", menu_title="ALL DAY")),
    "restaurant-level-three-e": (16, 1, dict(
        kind=F, title="The Prime Cut", subtitle="STEAKHOUSE", font="elephant", sign="board", sign_bg=(30, 22, 20),
        ink=(220, 190, 130), sign_trim=(150, 110, 60), wall="stone", wall_color=(90, 80, 74), front="classic",
        frame=(40, 26, 20), door="center", door_w=110, door_color=(60, 34, 24), interior="tables",
        tablecloth=(240, 240, 236), decor=["mirror", "frame", "shelf"], shelf_items=["bottle", "wine_glass"],
        closed="hanging", closed_plate=(30, 22, 20), closed_ink=(220, 190, 130), extras=["sconces"])),
    "restaurant-level-three-f": (16, 1, dict(
        kind=F, title="The Bavarian", subtitle="BEER HALL", font="gothic", sign="board", sign_bg=(240, 236, 220),
        ink=(30, 60, 120), sign_trim=(30, 90, 170), wall="planks", wall_color=(130, 90, 56), front="wood",
        frame=(60, 40, 26), door="left", door_w=110, door_color=(60, 40, 26), interior="tables_counter",
        counter_items=["beer_taps", "pint"], wood=(170, 120, 70), decor=["shelf", "frame"],
        shelf_items=["pint", "bottle"], awning=[(30, 90, 170), (245, 245, 240)], closed="placard",
        closed_lines=("CLOSED", "CHEERS!"))),

    # ------------------------------------------------------------ varejo nivel 3 (12 casas x 2 andares)
    "retail-level-three-a": (12, 2, dict(
        title="MAYFIELD'S", subtitle="DEPARTMENT STORE", font="bodoni", sign="board", sign_bg=(30, 40, 60),
        ink=(230, 210, 150), sign_trim=(200, 180, 120), wall="stone", wall_color=(170, 160, 140), front="classic",
        frame=(30, 40, 60), door="center", door_w=150, items=["mannequin", "purse", "shoe"], display="floor",
        upper_items=["mannequin"], upper_display="floor", awning=[(30, 40, 60)], closed="grille", extras=["flag"],
        flag=(30, 40, 60))),
    "retail-level-three-b": (12, 2, dict(
        title="Nordic Living", subtitle="FURNITURE & DESIGN", font="gill", sign="letters", ink=(240, 240, 236),
        wall="planks", wall_color=(130, 120, 110), front="modern", frame=(30, 30, 30), door="right",
        items=["sofa", "floor_lamp", "armchair"], display="floor", upper_items=["armchair", "floor_lamp", "pot_plant"],
        upper_display="floor", closed="placard", closed_lines=("CLOSED",))),
    "retail-level-three-c": (12, 2, dict(
        title="MEGA TECH", subtitle="ELECTRONICS SUPERSTORE", font="impact", sign="board", sign_bg=(220, 40, 30),
        ink=(255, 255, 255), wall="panels", wall_color=(60, 64, 76), front="modern", frame=(220, 40, 30),
        door="sides", door_w=110, items=["tv", "laptop", "phone"], shelves=2, upper_items=["tv"], closed="grille",
        upper_banner="BIG SAVINGS ON EVERYTHING")),
    "retail-level-three-d": (12, 2, dict(
        title="Market Fresh", subtitle="GOURMET GROCERS", font="cooper", sign="board", sign_bg=(40, 90, 50),
        ink=(250, 240, 200), wall="brick", wall_color=(150, 90, 60), front="wood", frame=(40, 90, 50), door="left",
        door_w=120, items=["fruit_crate", "grocery", "bottle", "cheese"], shelves=2,
        upper_items=["bottle", "box", "can"], awning=[(40, 90, 50), (240, 236, 220)], closed="shutter_half",
        shutter_drop=0.4, extras=["planters"])),
    "retail-level-three-e": (12, 2, dict(
        title="Maison Élise", font="vivaldi", sign="letters", ink=(255, 235, 215), font_size=54, wall="marble",
        wall_color=(40, 36, 40), front="arch", frame=(190, 160, 110), door="center", items=["mannequin"],
        display="floor", upper_items=["mannequin", "purse"], upper_display="floor", closed="placard",
        closed_lines=("CLOSED",), extras=["sconces"])),
    "retail-level-three-f": (12, 2, dict(
        title="TOY TOWN", font="showcard", sign="marquee", sign_bg=(250, 200, 40), ink=(220, 40, 60),
        wall="stripes", wall_color=(80, 150, 220), wall_color2=(250, 240, 120), front="modern", frame=(220, 40, 60),
        door="center", items=["teddy", "blocks", "ball"], shelves=2, upper_items=["teddy", "blocks", "beach_ball"],
        awning=[(220, 40, 60), (250, 240, 200)], closed="easel", closed_lines=("CLOSED", "toys are", "asleep!"))),
    "retail-level-three-g": (12, 2, dict(
        title="PRO SPORTS", subtitle="SPORTING GOODS", font="stencil", sign="board", sign_bg=(20, 60, 40),
        ink=(250, 250, 250), wall="panels", wall_color=(90, 96, 100), front="modern", frame=(250, 120, 30),
        door="right", door_w=110, items=["bike", "ball", "racket", "sport_shoe"], display="floor",
        upper_items=["sport_shoe", "ball", "racket"], closed="grille_door")),

    # ------------------------------------------------------------ varejo nivel 5 (32 casas x 2 andares)
    "retail-level-five-a": (32, 2, dict(
        title="VALENTINO ROSSI", subtitle="DESIGNER COLLECTION", font="elegant", sign="letters",
        ink=(250, 235, 190), sign_w=1200, sign_h=70, font_size=62, wall="marble", wall_color=(30, 30, 34), front="classic",
        frame=(190, 160, 100), door="center", door_w=180, items=["mannequin", "purse", "shoe"], display="floor",
        upper_items=["mannequin"], upper_display="floor", closed="placard", closed_lines=("CLOSED",),
        extras=["sconces", "pots"])),
    "retail-level-five-b": (32, 2, dict(
        title="GALAXY ARCADE", subtitle="GAMES  ·  PRIZES  ·  FUN", font="ravie", sign="neon",
        ink=(80, 220, 255), sign_w=1300, sign_h=80, wall="panels", wall_color=(30, 24, 50), front="modern",
        frame=(200, 60, 220), door="sides", door_w=140, items=["arcade"], display="floor", upper_items=["arcade"],
        upper_display="floor", closed="grille", upper_banner="HIGH SCORE CHALLENGE EVERY FRIDAY")),
}
