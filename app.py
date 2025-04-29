import random
from flask import Flask, render_template, request

app = Flask(__name__)

# --- Story Generation Logic (Simple Templates) ---

def generate_simple_story(characters, setting, story_type, language='en'):
    """Generates a story using simple templates and emojis."""

    # --- Basic Language Templates (Expand these!) ---
    # We'll use placeholders like {characters}, {setting}, {type_adj}
    # You would ideally have more varied templates per language.
    templates = {
        'en': [
            ("The Grand {type_adj} of {characters}",
             "Once upon a time, in the {adj} setting of {setting}, lived {characters}. {pronoun} embarked on a grand {type} quest, filled with {element1} and unexpected {element2}. ✨ Will they succeed? Only time will tell! 🥳"),
            ("A {type_adj} Day in {setting}",
             "Sunlight streamed into {setting} ☀️, illuminating the path for {characters}. It was the perfect day for a {type} adventure! They encountered {element1} and discovered a hidden {element2}. What a joyful journey! 😄"),
            ("{characters} and the Secret of {setting}",
             "Deep within {setting} lay a secret waiting to be found 🤫. {characters}, known for their bravery, took on the {type} challenge. They navigated tricky {element1} and finally uncovered the startling {element2}! 🎉"),
        ],
        'es': [
            ("La Gran {type_adj} de {characters}",
             "Érase una vez, en el {adj} lugar de {setting}, vivía(n) {characters}. {pronoun} se embarcó/embarcaron en una gran misión de {type}, llena de {element1} y {element2} inesperados. ✨ ¿Tendrán éxito? ¡Solo el tiempo lo dirá! 🥳"),
            ("Un Día {type_adj} en {setting}",
             "La luz del sol entraba en {setting} ☀️, iluminando el camino para {characters}. ¡Era el día perfecto para una aventura de {type}! Encontraron {element1} y descubrieron un(a) {element2} oculto(a). ¡Qué viaje tan alegre! 😄"),
            ("{characters} y el Secreto de {setting}",
             "En las profundidades de {setting} yacía un secreto esperando ser encontrado 🤫. {characters}, conocido(s) por su valentía, aceptó/aceptaron el desafío de {type}. ¡Navegaron por {element1} difíciles y finalmente descubrieron el/la sorprendente {element2}! 🎉"),
        ],
         'fr': [
            ("La Grande {type_adj} de {characters}",
             "Il était une fois, dans le décor {adj} de {setting}, vivaient {characters}. {pronoun} se lança/lancèrent dans une grande quête de {type}, remplie de {element1} et de {element2} inattendus. ✨ Réussiront-ils/elles ? Seul le temps nous le dira ! 🥳"),
            ("Une Journée {type_adj} à {setting}",
             "La lumière du soleil inondait {setting} ☀️, éclairant le chemin pour {characters}. C'était le jour parfait pour une aventure de {type} ! Ils/Elles rencontrèrent {element1} et découvrirent un(e) {element2} caché(e). Quelle joyeuse aventure ! 😄"),
            ("{characters} et le Secret de {setting}",
             "Au cœur de {setting} se cachait un secret 🤫. {characters}, connu(e)(s) pour leur bravoure, releva/relevèrent le défi de {type}. Ils/Elles naviguèrent à travers des {element1} délicats et découvrirent enfin le/la surprenant(e) {element2} ! 🎉"),
        ],
        'de': [
            ("Das große {type_adj} von {characters}",
             "Es war einmal, in der {adj} Umgebung von {setting}, lebte(n) {characters}. {pronoun} begab(en) sich auf eine große {type}-Quest, voller {element1} und unerwarteter {element2}. ✨ Werden sie Erfolg haben? Nur die Zeit wird es zeigen! 🥳"),
            ("Ein {type_adj} Tag in {setting}",
             "Sonnenlicht strömte nach {setting} ☀️ und erhellte den Weg für {characters}. Es war der perfekte Tag für ein {type}-Abenteuer! Sie begegneten {element1} und entdeckten ein(e) versteckte(s) {element2}. Welch fröhliche Reise! 😄"),
            ("{characters} und das Geheimnis von {setting}",
             "Tief in {setting} lag ein Geheimnis verborgen 🤫. {characters}, bekannt für ihre Tapferkeit, nahm(en) die {type}-Herausforderung an. Sie navigierten durch knifflige {element1} und enthüllten schließlich das überraschende {element2}! 🎉"),
        ],
        'it': [
            ("La Grande {type_adj} di {characters}",
             "C'era una volta, nell'ambiente {adj} di {setting}, viveva/vivevano {characters}. {pronoun} si imbarcò/imbarcarono in una grande missione di {type}, piena di {element1} e {element2} inaspettati. ✨ Riusciranno nell'impresa? Solo il tempo lo dirà! 🥳"),
            ("Una Giornata {type_adj} a {setting}",
             "La luce del sole inondava {setting} ☀️, illuminando il cammino per {characters}. Era il giorno perfetto per un'avventura di {type}! Incontrarono {element1} e scoprirono un(a) {element2} nascosto(a). Che viaggio gioioso! 😄"),
            ("{characters} e il Segreto di {setting}",
             "Nel profondo di {setting} si nascondeva un segreto 🤫. {characters}, noto/i per il loro coraggio, accettò/accettarono la sfida di {type}. Navigarono attraverso {element1} difficili e alla fine scoprirono il/la sorprendente {element2}! 🎉"),
        ],
         'pt': [
            ("A Grande {type_adj} de {characters}",
             "Era uma vez, no cenário {adj} de {setting}, vivia(m) {characters}. {pronoun} embarcou/embarcaram numa grande jornada de {type}, cheia de {element1} e {element2} inesperados. ✨ Terão sucesso? Só o tempo dirá! 🥳"),
            ("Um Dia {type_adj} em {setting}",
             "A luz do sol entrava em {setting} ☀️, iluminando o caminho para {characters}. Era o dia perfeito para uma aventura de {type}! Encontraram {element1} e descobriram um(a) {element2} escondido(a). Que jornada alegre! 😄"),
            ("{characters} e o Segredo de {setting}",
             "Nas profundezas de {setting} escondia-se um segredo 🤫. {characters}, conhecido(s) pela sua bravura, aceitou/aceitaram o desafio de {type}. Navegaram por {element1} complicados e finalmente descobriram o/a surpreendente {element2}! 🎉"),
        ],
        # Add other languages here...
    }

    # Fallback to English if language not found
    if language not in templates:
        language = 'en'

    # --- Define elements based on story type ---
    type_elements = {
        'en': {
            'Adventure': (["exciting challenges 🧗", "daring escapes 🏃💨", "mysterious maps 🗺️"], ["ancient ruins 🏛️", "sparkling treasure 💎", "a hidden portal ✨"]),
            'Romance': (["stolen glances 👀", "heartfelt confessions 💌", "a moonlit dance 🌕"], ["a blossoming flower 🌹", "a promised future 💍", "true love's kiss 😘"]),
            'Mystery': (["cryptic clues ❓", "suspicious whispers 🤫", "locked doors 🔒"], ["a forgotten diary 📖", "a hidden motive 💡", "the real culprit 👤"]),
            'Fantasy': (["magical spells ✨", "mythical creatures 🐉", "enchanted forests 🌳"], ["a powerful artifact 💍", "a prophecy foretold 📜", "a dragon's hoard 💰"]),
            'Sci-Fi': (["laser battles 🔫", "hyperspace jumps 🚀", "alien encounters 👽"], ["an advanced AI 🤖", "a distant galaxy 🌌", "a time paradox ⏳"]),
            'Humor': (["silly misunderstandings 😂", "wacky inventions 🤪", "unexpected punchlines 💥"], ["a rubber chicken 🐔", "a pie in the face 🥧", "a talking squirrel 🐿️"]),
            'Fairy Tale': (["a fairy godmother 🧚", "talking animals 🦉", "a royal ball 👑"], ["a glass slipper 👠", "a magic beanstalk 🌱", "happily ever after 💖"]),
        },
         'es': { # Example Spanish translations
            'Adventure': (["desafíos emocionantes 🧗", "huidas audaces 🏃💨", "mapas misteriosos 🗺️"], ["ruinas antiguas 🏛️", "tesoros brillantes 💎", "un portal oculto ✨"]),
            'Romance': (["miradas robadas 👀", "confesiones sinceras 💌", "un baile bajo la luna 🌕"], ["una flor que florece 🌹", "un futuro prometido 💍", "el beso del amor verdadero 😘"]),
            'Mystery': (["pistas crípticas ❓", "susurros sospechosos 🤫", "puertas cerradas 🔒"], ["un diario olvidado 📖", "un motivo oculto 💡", "el verdadero culpable 👤"]),
            'Fantasy': (["hechizos mágicos ✨", "criaturas míticas 🐉", "bosques encantados 🌳"], ["un artefacto poderoso 💍", "una profecía anunciada 📜", "el tesoro de un dragón 💰"]),
            'Sci-Fi': (["batallas láser 🔫", "saltos al hiperespacio 🚀", "encuentros alienígenas 👽"], ["una IA avanzada 🤖", "una galaxia lejana 🌌", "una paradoja temporal ⏳"]),
            'Humor': (["malentendidos tontos 😂", "inventos locos 🤪", "remates inesperados 💥"], ["un pollo de goma 🐔", "una tarta en la cara 🥧", "una ardilla parlante 🐿️"]),
            'Fairy Tale': (["un hada madrina 🧚", "animales parlantes 🦉", "un baile real 👑"], ["una zapatilla de cristal 👠", "un tallo de frijol mágico 🌱", "felices para siempre 💖"]),
        },
        # Add translated elements for fr, de, it, pt...
         'fr': {
            'Adventure': (["défis passionnants 🧗", "évasions audacieuses 🏃💨", "cartes mystérieuses 🗺️"], ["ruines antiques 🏛️", "trésors étincelants 💎", "un portail caché ✨"]),
            'Romance': (["regards volés 👀", "confessions sincères 💌", "une danse au clair de lune 🌕"], ["une fleur épanouie 🌹", "un avenir promis 💍", "le baiser du véritable amour 😘"]),
            'Mystery': (["indices cryptiques ❓", "murmures suspects 🤫", "portes verrouillées 🔒"], ["un journal oublié 📖", "un mobile caché 💡", "le vrai coupable 👤"]),
            'Fantasy': (["sorts magiques ✨", "créatures mythiques 🐉", "forêts enchantées 🌳"], ["un artefact puissant 💍", "une prophétie annoncée 📜", "le trésor d'un dragon 💰"]),
            'Sci-Fi': (["batailles laser 🔫", "sauts hyperspatiaux 🚀", "rencontres extraterrestres 👽"], ["une IA avancée 🤖", "une galaxie lointaine 🌌", "un paradoxe temporel ⏳"]),
            'Humor': (["quiproquos idiots 😂", "inventions farfelues 🤪", "chutes inattendues 💥"], ["un poulet en caoutchouc 🐔", "une tarte à la crème 🥧", "un écureuil parlant 🐿️"]),
            'Fairy Tale': (["une fée marraine 🧚", "animaux parlants 🦉", "un bal royal 👑"], ["une pantoufle de verre 👠", "un haricot magique 🌱", "ils vécurent heureux 💖"]),
        },
        'de': {
            'Adventure': (["spannende Herausforderungen 🧗", "kühne Fluchten 🏃💨", "mysteriöse Karten 🗺️"], ["antike Ruinen 🏛️", "funkelnde Schätze 💎", "ein verstecktes Portal ✨"]),
            'Romance': (["gestohlene Blicke 👀", "herzliche Geständnisse 💌", "ein Tanz im Mondschein 🌕"], ["eine blühende Blume 🌹", "eine versprochene Zukunft 💍", "der Kuss der wahren Liebe 😘"]),
            'Mystery': (["kryptische Hinweise ❓", "verdächtiges Flüstern 🤫", "verschlossene Türen 🔒"], ["ein vergessenes Tagebuch 📖", "ein verborgenes Motiv 💡", "der wahre Schuldige 👤"]),
            'Fantasy': (["magische Zauber ✨", "mythische Kreaturen 🐉", "verwunschene Wälder 🌳"], ["ein mächtiges Artefakt 💍", "eine Prophezeiung 📜", "ein Drachenhort 💰"]),
            'Sci-Fi': (["Laserschlachten 🔫", "Hyperraumsprünge 🚀", "Alienbegegnungen 👽"], ["eine fortschrittliche KI 🤖", "eine ferne Galaxie 🌌", "ein Zeitparadoxon ⏳"]),
            'Humor': (["alberne Missverständnisse 😂", "verrückte Erfindungen 🤪", "unerwartete Pointen 💥"], ["ein Gummihuhn 🐔", "eine Torte ins Gesicht 🥧", "ein sprechendes Eichhörnchen 🐿️"]),
            'Fairy Tale': (["eine gute Fee 🧚", "sprechende Tiere 🦉", "ein königlicher Ball 👑"], ["ein gläserner Schuh 👠", "eine magische Bohnenranke 🌱", "glücklich bis ans Ende 💖"]),
        },
        'it': {
            'Adventure': (["sfide emozionanti 🧗", "fughe audaci 🏃💨", "mappe misteriose 🗺️"], ["rovine antiche 🏛️", "tesori scintillanti 💎", "un portale nascosto ✨"]),
            'Romance': (["sguardi rubati 👀", "confessioni sincere 💌", "un ballo al chiaro di luna 🌕"], ["un fiore che sboccia 🌹", "un futuro promesso 💍", "il bacio del vero amore 😘"]),
            'Mystery': (["indizi criptici ❓", "sussurri sospetti 🤫", "porte chiuse 🔒"], ["un diario dimenticato 📖", "un movente nascosto 💡", "il vero colpevole 👤"]),
            'Fantasy': (["incantesimi magici ✨", "creature mitiche 🐉", "foreste incantate 🌳"], ["un artefatto potente 💍", "una profezia annunciata 📜", "il tesoro di un drago 💰"]),
            'Sci-Fi': (["battaglie laser 🔫", "salti nell'iperspazio 🚀", "incontri alieni 👽"], ["un'IA avanzata 🤖", "una galassia lontana 🌌", "un paradosso temporale ⏳"]),
            'Humor': (["equivoci sciocchi 😂", "invenzioni stravaganti 🤪", "battute inaspettate 💥"], ["un pollo di gomma 🐔", "una torta in faccia 🥧", "uno scoiattolo parlante 🐿️"]),
            'Fairy Tale': (["una fata madrina 🧚", "animali parlanti 🦉", "un ballo reale 👑"], ["una scarpetta di vetro 👠", "una pianta di fagioli magica 🌱", "e vissero felici e contenti 💖"]),
        },
         'pt': {
            'Adventure': (["desafios emocionantes 🧗", "fugas ousadas 🏃💨", "mapas misteriosos 🗺️"], ["ruínas antigas 🏛️", "tesouros brilhantes 💎", "um portal escondido ✨"]),
            'Romance': (["olhares roubados 👀", "confissões sinceras 💌", "uma dança ao luar 🌕"], ["uma flor a desabrochar 🌹", "um futuro prometido 💍", "o beijo do amor verdadeiro 😘"]),
            'Mystery': (["pistas enigmáticas ❓", "sussurros suspeitos 🤫", "portas trancadas 🔒"], ["um diário esquecido 📖", "um motivo oculto 💡", "o verdadeiro culpado 👤"]),
            'Fantasy': (["feitiços mágicos ✨", "criaturas míticas 🐉", "florestas encantadas 🌳"], ["um artefato poderoso 💍", "uma profecia anunciada 📜", "o tesouro de um dragão 💰"]),
            'Sci-Fi': (["batalhas de laser 🔫", "saltos no hiperespaço 🚀", "encontros alienígenas 👽"], ["uma IA avançada 🤖", "uma galáxia distante 🌌", "um paradoxo temporal ⏳"]),
            'Humor': (["mal-entendidos bobos 😂", "invenções malucas 🤪", "piadas inesperadas 💥"], ["uma galinha de borracha 🐔", "uma torta na cara 🥧", "um esquilo falante 🐿️"]),
            'Fairy Tale': (["uma fada madrinha 🧚", "animais falantes 🦉", "um baile real 👑"], ["um sapatinho de cristal 👠", "um pé de feijão mágico 🌱", "felizes para sempre 💖"]),
        },
    }


    # --- Get type-specific adjectives and pronouns (basic) ---
    # This needs significant improvement for real grammatical accuracy per language
    type_adjectives = {
        'en': {'Adventure': 'thrilling', 'Romance': 'heartwarming', 'Mystery': 'puzzling', 'Fantasy': 'enchanted', 'Sci-Fi': 'cosmic', 'Humor': 'hilarious', 'Fairy Tale': 'magical'},
        'es': {'Adventure': 'emocionante', 'Romance': 'conmovedora', 'Mystery': 'desconcertante', 'Fantasy': 'encantada', 'Sci-Fi': 'cósmica', 'Humor': 'hilarante', 'Fairy Tale': 'mágica'},
        'fr': {'Adventure': 'palpitante', 'Romance': 'chaleureuse', 'Mystery': 'déroutante', 'Fantasy': 'enchantée', 'Sci-Fi': 'cosmique', 'Humor': 'hilarante', 'Fairy Tale': 'magique'},
        'de': {'Adventure': 'aufregenden', 'Romance': 'herzerwärmenden', 'Mystery': 'rätselhaften', 'Fantasy': 'verzauberten', 'Sci-Fi': 'kosmischen', 'Humor': 'urkomischen', 'Fairy Tale': 'magischen'},
        'it': {'Adventure': 'emozionante', 'Romance': 'commovente', 'Mystery': 'sconcertante', 'Fantasy': 'incantata', 'Sci-Fi': 'cosmica', 'Humor': 'esilarante', 'Fairy Tale': 'magica'},
        'pt': {'Adventure': 'emocionante', 'Romance': 'comovente', 'Mystery': 'intrigante', 'Fantasy': 'encantada', 'Sci-Fi': 'cósmica', 'Humor': 'hilariante', 'Fairy Tale': 'mágica'},
    }
    setting_adjectives = {
        'en': ['whimsical', 'bustling', 'serene', 'mysterious', 'futuristic', 'charming'],
        'es': ['caprichoso', 'bullicioso', 'sereno', 'misterioso', 'futurista', 'encantador'],
        'fr': ['fantasque', 'animé', 'serein', 'mystérieux', 'futuriste', 'charmant'],
        'de': ['launischen', 'belebten', 'ruhigen', 'mysteriösen', 'futuristischen', 'charmanten'],
        'it': ['stravagante', 'vivace', 'sereno', 'misterioso', 'futuristico', 'affascinante'],
        'pt': ['caprichoso', 'movimentado', 'sereno', 'misterioso', 'futurista', 'charmoso'],
    }
    # VERY basic pronoun handling - assumes plural if 'and' or ',' is in names
    pronouns = {
        'en': ('They', 'them'), 'es': ('Ellos/Ellas', 'ellos/ellas'), 'fr': ('Ils/Elles', 'eux/elles'),
        'de': ('Sie', 'sie'), 'it': ('Loro', 'loro'), 'pt': ('Eles/Elas', 'eles/elas')
    }
    if ' and ' in characters or ',' in characters:
        pronoun = pronouns.get(language, pronouns['en'])[0]
    else:
        # Default to singular - needs gender detection for many languages!
         pronoun = pronouns.get(language, pronouns['en'])[0] # Using plural for simplicity now


    # --- Select Random Elements ---
    chosen_template = random.choice(templates.get(language, templates['en']))
    lang_elements = type_elements.get(language, type_elements['en'])
    elements1 = lang_elements.get(story_type, lang_elements['Adventure'])[0]
    elements2 = lang_elements.get(story_type, lang_elements['Adventure'])[1]
    element1 = random.choice(elements1)
    element2 = random.choice(elements2)
    type_adj = type_adjectives.get(language, type_adjectives['en']).get(story_type, 'amazing')
    setting_adj = random.choice(setting_adjectives.get(language, setting_adjectives['en']))


    # --- Format the story ---
    story_title = chosen_template[0].format(
        characters=characters,
        setting=setting,
        type=story_type,
        type_adj=type_adj,
        adj=setting_adj,
        pronoun=pronoun,
        element1=element1,
        element2=element2,
    )
    story_body = chosen_template[1].format(
        characters=f"**{characters}**", # Make names bold
        setting=f"*{setting}*", # Make setting italic
        type=story_type,
        type_adj=type_adj,
        adj=setting_adj,
        pronoun=pronoun,
        element1=element1,
        element2=element2,
    )

    # Simple markdown-like bold/italic to HTML
    story_body = story_body.replace("**", "<strong>").replace("*", "<em>")

    return story_title, story_body

# --- Flask Routes ---

@app.route('/')
def index():
    """Displays the main input form."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_story():
    """Handles form submission and displays the generated story."""
    try:
        characters = request.form['characters']
        setting = request.form['setting']
        story_type = request.form['type']
        language = request.form['language']

        # Basic input validation (can be more robust)
        if not characters or not setting or not story_type or not language:
             raise ValueError("Missing input fields")

        # --- Generate Story ---
        story_title, story_body = generate_simple_story(characters, setting, story_type, language)


        return render_template('result.html',
                               story_title=story_title,
                               story_body=story_body)
    except Exception as e:
        print(f"Error generating story: {e}") # Log error for debugging
        # You could redirect back to index with an error message
        # from flask import flash, redirect, url_for
        # flash(f"Oops! Something went wrong: {e}", 'error')
        # return redirect(url_for('index'))
        # Or show a generic error page:
        return render_template('result.html',
                               story_title="Oh no! 😟",
                               story_body="Something went a bit wobbly generating your story. Please check your inputs and try again! ✨")


# --- Main Execution ---
if __name__ == '__main__':
    # Use debug=True only for local development, not production
    app.run(debug=True)
    # For production with gunicorn: gunicorn app:app
