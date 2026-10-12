"""Extra data: styles, colors, seasons, quiz, capsule builder, checklist."""

# per outfit: seasons, one style, colors
ATTRS = {
    "fall-capsule-brown-tones":   dict(seasons=["fall", "winter"], style="quiet",   colors=["brown", "cream"]),
    "white-button-down":          dict(seasons=["spring", "summer", "fall"], style="classic", colors=["cream", "brown"]),
    "leather-blazer":             dict(seasons=["fall", "spring"], style="edge",    colors=["brown", "cream"]),
    "leather-trench-knit-dress":  dict(seasons=["fall", "winter"], style="edge",    colors=["brown", "cream"]),
    "cream-shirt-white-trousers": dict(seasons=["spring", "summer"], style="classic", colors=["cream"]),
    "barrel-leg-jeans":           dict(seasons=["fall", "spring"], style="edge",    colors=["denim", "brown"]),
    "mock-neck-bodysuit":         dict(seasons=["fall", "winter", "spring"], style="quiet", colors=["brown", "cream"]),
    "neutral-trench-tall-boots":  dict(seasons=["fall", "spring"], style="quiet",   colors=["cream"]),
    "wide-leg-jeans-cuff":        dict(seasons=["spring", "fall"], style="edge",    colors=["denim"]),
    "linen-blazer-shorts-set":    dict(seasons=["summer", "spring"], style="classic", colors=["cream"]),
    "brown-knit-pleated-trousers": dict(seasons=["fall", "spring"], style="classic", colors=["brown", "grey"]),
    "knitwear-essentials":        dict(seasons=["fall", "winter"], style="classic", colors=["cream", "brown", "grey"]),
    "oversized-mock-neck-sweater": dict(seasons=["fall", "winter"], style="quiet",  colors=["brown", "cream"]),
    "grey-v-neck-knit":           dict(seasons=["fall", "winter", "spring"], style="classic", colors=["grey"]),
    "belted-wool-coat":           dict(seasons=["winter", "fall"], style="quiet",    colors=["grey"]),
    "cream-blouse-contrast-trim": dict(seasons=["spring", "summer", "fall"], style="soft", colors=["cream", "brown"]),
    "office-siren":               dict(seasons=["fall", "winter"], style="edge",    colors=["grey"]),
    "coquette-bow-blouse":        dict(seasons=["spring", "summer"], style="soft", colors=["cream", "brown"]),
    "silk-scarf-styling":         dict(seasons=["fall", "spring"], style="soft",    colors=["grey"]),
    "cream-vest-mini-skirt":      dict(seasons=["spring", "summer", "fall"], style="soft", colors=["cream", "brown"]),
    "lace-skirt-brown-knit":      dict(seasons=["fall", "winter"], style="soft",    colors=["brown"]),
}

COLORS = [("brown", "Brown"), ("cream", "Cream & white"), ("grey", "Grey"), ("denim", "Denim")]
SIZES = [("regular", "Regular", ""), ("petite", "Petite", "petite"), ("plus", "Plus size", "plus size"), ("tall", "Tall", "tall")]

STYLES = {
    "classic": ("Classic Minimalist", "Crisp shirts, clean lines and neutral tones. You like pieces that always work and never date."),
    "quiet":   ("Quiet Luxury", "Rich textures, warm browns and cream. Understated, soft and expensive-looking."),
    "soft":    ("Soft Romantic", "Bows, silk and lace details. Feminine touches, kept office-appropriate."),
    "edge":    ("Modern Edge", "Leather, structure and sharp tailoring. Confident, polished and a little bold."),
}

# (id, title, blurb, hero pin id)
SEASONS = [
    ("fall", "Fall", "Rich browns, warm layers and cozy knits.", "632966922682369892"),
    ("winter", "Winter", "Wool coats, soft knitwear and tonal dressing.", "632966922682352597"),
    ("spring", "Spring", "Trenches, crisp shirts and light layers.", "632966922682359264"),
    ("summer", "Summer", "Linen, light tailoring and easy sets.", "632966922682352730"),
]

# 8 pieces per season: (name, amazon query, cap in dollars for the budget link)
CAPSULES = {
    "fall": [("Brown wool blend coat", "women brown wool blend coat", 90),
             ("Chocolate mock neck sweater", "women chocolate brown mock neck sweater", 40),
             ("Cream ribbed turtleneck", "women cream ribbed turtleneck", 35),
             ("Tailored brown trousers", "women brown tailored trousers", 50),
             ("Suede-look midi skirt", "women faux suede midi skirt", 45),
             ("Dark wash barrel jeans", "women dark wash barrel leg jeans", 55),
             ("Leather-look blazer", "women faux leather blazer", 70),
             ("Brown loafers or boots", "women brown loafers", 60)],
    "winter": [("Belted wool coat", "women belted wool blend wrap coat", 100),
               ("Classic turtleneck", "women turtleneck sweater", 40),
               ("Grey V-neck sweater", "women grey v neck sweater", 40),
               ("Wool-blend trousers", "women wool blend trousers", 60),
               ("Ribbed knit midi dress", "women ribbed knit midi dress", 50),
               ("Knit cardigan", "women button front cardigan", 45),
               ("Warm tights", "women fleece lined tights", 20),
               ("Ankle boots", "women ankle boots work", 70)],
    "spring": [("Beige trench coat", "women beige trench coat", 80),
               ("White button down", "women white button down shirt", 35),
               ("Light blazer", "women oatmeal blazer", 60),
               ("Wide-leg trousers", "women cream wide leg trousers", 50),
               ("Midi skirt", "women midi skirt work", 40),
               ("Silk-feel blouse", "women satin blouse work", 35),
               ("Silk scarf", "women silk scarf", 25),
               ("Loafers", "women loafers", 60)],
    "summer": [("Linen blazer", "women linen blazer", 60),
               ("Linen trousers", "women linen trousers", 45),
               ("Tailored shorts", "women tailored linen shorts", 35),
               ("Sleeveless knit top", "women sleeveless knit top", 30),
               ("White shirt", "women white button down shirt", 35),
               ("Midi shirt dress", "women midi shirt dress", 50),
               ("Flat sandals", "women leather flat sandals", 45),
               ("Structured tote", "women work tote bag", 50)],
}

QUIZ = [
    ("Pick your office staple", [("classic", "A crisp white shirt"), ("quiet", "A cozy fine knit"), ("soft", "A silk bow blouse"), ("edge", "A leather-look blazer")]),
    ("Choose your palette", [("classic", "White, cream and grey"), ("quiet", "Chocolate, camel and cream"), ("soft", "Soft neutrals with a hint of lace"), ("edge", "Charcoal, black and deep brown")]),
    ("Your office dress code", [("classic", "Smart casual"), ("quiet", "Relaxed but polished"), ("soft", "Creative and flexible"), ("edge", "Corporate and sharp")]),
    ("Favorite finishing touch", [("classic", "A slim leather belt"), ("quiet", "A quality leather bag"), ("soft", "A silk scarf"), ("edge", "Statement boots")]),
    ("Your Monday mood", [("classic", "Organized and ready"), ("quiet", "Calm and cozy"), ("soft", "Romantic and soft"), ("edge", "Confident and bold")]),
]

# capsule builder: (id, group, name, amazon query, cap)
BUILDER = [
    ("p1", "tops", "White button down", "women white button down shirt", 35),
    ("p2", "tops", "Cream fine knit", "women cream fine knit sweater", 35),
    ("p3", "tops", "Turtleneck", "women turtleneck sweater", 35),
    ("p4", "tops", "Silk-feel blouse", "women satin blouse work", 35),
    ("p5", "tops", "Mock neck bodysuit", "women mock neck bodysuit", 30),
    ("p6", "bottoms", "Tailored trousers", "women tailored work trousers", 50),
    ("p7", "bottoms", "Wide-leg trousers", "women wide leg trousers work", 50),
    ("p8", "bottoms", "Midi skirt", "women midi skirt work", 40),
    ("p9", "bottoms", "Dark jeans", "women dark wash straight jeans", 55),
    ("p10", "layers", "Classic blazer", "women classic blazer work", 60),
    ("p11", "layers", "Trench coat", "women trench coat beige", 80),
    ("p12", "layers", "Wool coat", "women wool blend coat", 100),
    ("p13", "dresses", "Knit midi dress", "women knit midi dress", 50),
    ("p14", "dresses", "Shirt dress", "women midi shirt dress", 50),
    ("p15", "shoes", "Loafers", "women loafers", 60),
    ("p16", "shoes", "Ankle boots", "women ankle boots work", 70),
]
BUILDER_GROUPS = [("tops", "Tops"), ("bottoms", "Bottoms"), ("layers", "Layers"), ("dresses", "Dresses"), ("shoes", "Shoes")]

CHECKLIST = [
    "A classic blazer", "A crisp white button down", "Tailored trousers", "Wide-leg trousers",
    "A midi skirt", "A fine-gauge knit sweater", "A turtleneck or mock neck", "A work dress",
    "A neutral trench or coat", "Dark wash jeans for casual days", "Loafers or flats", "A structured bag",
]
