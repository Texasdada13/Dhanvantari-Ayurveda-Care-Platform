"""
Seed script — inserts classical Ayurvedic supplements and recipes.
Run from the backend/ directory:
    python scripts/seed.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.plan import Supplement, Recipe

# ── Supplements ───────────────────────────────────────────────────────────────

SUPPLEMENTS = [
    # ── Adaptogenic / Rejuvenative ────────────────────────────────────────────
    dict(name="Ashwagandha", name_sanskrit="Withania somnifera", category="Adaptogenic",
         dosha_effect="Reduces Vata, balances Pitta", is_classical=True,
         typical_dose="500–1000 mg or 1 tsp churna",
         purpose="Adaptogen, stress relief, strength, thyroid support, immune tonic",
         cautions="Avoid in high Pitta, hyperthyroidism (use cautiously). Avoid in pregnancy."),

    dict(name="Shatavari", name_sanskrit="Asparagus racemosus", category="Rejuvenative",
         dosha_effect="Reduces Vata and Pitta, may increase Kapha", is_classical=True,
         typical_dose="500–1000 mg or 1 tsp churna",
         purpose="Female reproductive tonic, hormonal balance, lactation support, gut soothing",
         cautions="May increase Kapha if used in excess. Avoid with estrogen-sensitive conditions."),

    dict(name="Amalaki", name_sanskrit="Emblica officinalis", category="Rejuvenative",
         dosha_effect="Tridoshic — balances all three doshas", is_classical=True,
         typical_dose="500 mg – 1g or 1 tsp churna",
         purpose="Vitamin C powerhouse, liver tonic, skin, hair, digestion, anti-aging (Rasayana)",
         cautions="May cause loose stools in high doses. Best taken with honey or ghee."),

    dict(name="Brahmi", name_sanskrit="Bacopa monnieri", category="Nervine",
         dosha_effect="Reduces Vata and Pitta, neutral for Kapha", is_classical=True,
         typical_dose="300–500 mg or 1/2 tsp churna",
         purpose="Memory, cognitive function, anxiety, ADHD, stress, sleep quality",
         cautions="May slow heart rate in very high doses. Start low."),

    dict(name="Shankhapushpi", name_sanskrit="Convolvulus pluricaulis", category="Nervine",
         dosha_effect="Reduces Vata and Pitta", is_classical=True,
         typical_dose="3–6g of whole herb or 250–500 mg extract",
         purpose="Brain tonic, anxiety, insomnia, hypertension",
         cautions="Avoid with phenytoin (reduces drug absorption)."),

    dict(name="Guduchi", name_sanskrit="Tinospora cordifolia", category="Immunomodulator",
         dosha_effect="Tridoshic — especially good for Pitta", is_classical=True,
         typical_dose="300–500 mg or 1 tsp churna",
         purpose="Immunity, fever, liver support, inflammation, blood sugar",
         cautions="May lower blood sugar — monitor if on diabetes medication."),

    dict(name="Triphala", name_sanskrit="Amalaki + Bibhitaki + Haritaki", category="Digestive",
         dosha_effect="Tridoshic", is_classical=True,
         typical_dose="500 mg – 1g or 1 tsp churna before bed",
         purpose="Bowel regulator, colon cleanser, gentle laxative, detox, eye health",
         cautions="Avoid during pregnancy. May cause loose stools if dose too high."),

    dict(name="Trikatu", name_sanskrit="Ginger + Black Pepper + Pippali", category="Digestive",
         dosha_effect="Reduces Kapha and Vata, increases Pitta (use cautiously)", is_classical=True,
         typical_dose="250–500 mg before meals",
         purpose="Kindles Agni (digestive fire), fat metabolism, respiratory, Ama-burning",
         cautions="Avoid if high Pitta, GERD, or ulcers."),

    dict(name="Dashamula", name_sanskrit="Ten Root Formula", category="Vata-pacifying",
         dosha_effect="Reduces Vata, mild Kapha", is_classical=True,
         typical_dose="1 tsp powder in warm water or decoction",
         purpose="Joint pain, nerve tonic, lower back pain, postpartum recovery",
         cautions="Best used under practitioner guidance. Avoid in pregnancy."),

    dict(name="Haritaki", name_sanskrit="Terminalia chebula", category="Digestive",
         dosha_effect="Reduces all doshas, especially Vata", is_classical=True,
         typical_dose="500 mg – 1g with warm water",
         purpose="Constipation, digestion, detox, anti-parasitic, respiratory",
         cautions="Avoid during pregnancy and severe dehydration."),

    dict(name="Bibhitaki", name_sanskrit="Terminalia bellirica", category="Respiratory",
         dosha_effect="Reduces Kapha mainly, mild Pitta and Vata", is_classical=True,
         typical_dose="500 mg – 1g",
         purpose="Respiratory tract, mucus clearing, voice, cholesterol",
         cautions="Avoid in severe dryness or dehydration."),

    dict(name="Licorice Root (Yashtimadhu)", name_sanskrit="Glycyrrhiza glabra", category="Adaptogenic",
         dosha_effect="Reduces Vata and Pitta, increases Kapha", is_classical=True,
         typical_dose="250–500 mg or 1/2 tsp",
         purpose="Adrenal support, gut healing, gastric ulcer, sore throat, cortisol balance",
         cautions="Avoid with hypertension, edema, kidney disease, or long-term use > 4 weeks without break."),

    dict(name="Turmeric (Haridra)", name_sanskrit="Curcuma longa", category="Anti-inflammatory",
         dosha_effect="Tridoshic, especially reduces Kapha", is_classical=True,
         typical_dose="500–1000 mg or 1 tsp with black pepper + fat",
         purpose="Anti-inflammatory, liver, skin, blood purifier, joint pain",
         cautions="High doses may thin blood. Avoid before surgery."),

    dict(name="Neem (Nimba)", name_sanskrit="Azadirachta indica", category="Detox",
         dosha_effect="Reduces Pitta and Kapha", is_classical=True,
         typical_dose="250–500 mg",
         purpose="Blood purifier, skin conditions, anti-microbial, blood sugar",
         cautions="Very bitter. Avoid in pregnancy and while trying to conceive. Cold in nature."),

    dict(name="Punarnava", name_sanskrit="Boerhavia diffusa", category="Diuretic/Kidney",
         dosha_effect="Reduces Kapha and Pitta", is_classical=True,
         typical_dose="500 mg – 1g",
         purpose="Kidney support, edema/water retention, liver, inflammation",
         cautions="Monitor potassium levels if on diuretics."),

    dict(name="Gokshura (Tribulus)", name_sanskrit="Tribulus terrestris", category="Urinary/Reproductive",
         dosha_effect="Reduces Vata and Pitta", is_classical=True,
         typical_dose="500 mg – 1g",
         purpose="Kidney stones, urinary tract, libido, testosterone, prostate",
         cautions="Avoid in pregnancy. May interact with diabetes and BP medications."),

    dict(name="Manjistha", name_sanskrit="Rubia cordifolia", category="Detox",
         dosha_effect="Reduces Pitta and Kapha", is_classical=True,
         typical_dose="500 mg – 1g",
         purpose="Blood purifier, skin (acne, psoriasis), lymphatic, liver",
         cautions="May turn urine orange/red — harmless. Avoid large doses in pregnancy."),

    dict(name="Vidanga", name_sanskrit="Embelia ribes", category="Digestive/Anti-parasitic",
         dosha_effect="Reduces Vata and Kapha", is_classical=True,
         typical_dose="250–500 mg",
         purpose="Intestinal parasites, Ama-burning, constipation, skin",
         cautions="Avoid in pregnancy. High doses can be irritating."),

    dict(name="Kutki (Picrorhiza)", name_sanskrit="Picrorhiza kurroa", category="Liver/Digestive",
         dosha_effect="Reduces Pitta and Kapha", is_classical=True,
         typical_dose="200–400 mg",
         purpose="Liver tonic, hepatitis support, inflammation, fever, digestion",
         cautions="Very bitter. May cause nausea in sensitive individuals."),

    dict(name="Bhumyamalaki", name_sanskrit="Phyllanthus niruri", category="Liver",
         dosha_effect="Reduces Pitta and Kapha", is_classical=True,
         typical_dose="400–600 mg",
         purpose="Liver disease, gallstones, kidney stones, hepatitis B support",
         cautions="Avoid in pregnancy."),

    dict(name="Arjuna", name_sanskrit="Terminalia arjuna", category="Cardiovascular",
         dosha_effect="Reduces Kapha and Pitta", is_classical=True,
         typical_dose="500 mg – 1g",
         purpose="Heart tonic, blood pressure, cholesterol, angina",
         cautions="May interact with cardiac medications. Monitor BP."),

    dict(name="Garlic (Lasuna)", name_sanskrit="Allium sativum", category="Cardiovascular",
         dosha_effect="Reduces Kapha and Vata, may increase Pitta", is_classical=True,
         typical_dose="500 mg or 1–2 raw cloves",
         purpose="Heart health, cholesterol, antimicrobial, blood thinning",
         cautions="Avoid before surgery. May interact with blood thinners."),

    dict(name="Guggulu", name_sanskrit="Commiphora mukul", category="Detox/Joint",
         dosha_effect="Reduces all doshas, especially Kapha", is_classical=True,
         typical_dose="500 mg – 1g",
         purpose="Cholesterol, thyroid (stimulates T4→T3), weight loss, joint pain, detox",
         cautions="Avoid in pregnancy. May interact with blood thinners and thyroid medications."),

    dict(name="Sarpagandha", name_sanskrit="Rauvolfia serpentina", category="Nervine",
         dosha_effect="Reduces Vata and Pitta", is_classical=True,
         typical_dose="250–500 mg",
         purpose="Hypertension, insomnia, anxiety, psychiatric conditions",
         cautions="Avoid with depression medications (MAOI interaction). Use only under supervision."),

    dict(name="Jatamansi", name_sanskrit="Nardostachys jatamansi", category="Nervine",
         dosha_effect="Reduces Vata and Pitta", is_classical=True,
         typical_dose="250–500 mg",
         purpose="Anxiety, insomnia, depression, memory, epilepsy support",
         cautions="Endangered plant — use ethically sourced only. Avoid in pregnancy."),

    dict(name="Bala", name_sanskrit="Sida cordifolia", category="Vata-pacifying",
         dosha_effect="Reduces Vata and Pitta", is_classical=True,
         typical_dose="500 mg – 1g",
         purpose="Nerve tonic, weakness, muscle building, joint support",
         cautions="Contains ephedrine alkaloids — avoid with heart conditions or hypertension."),

    dict(name="Chyawanprash", name_sanskrit="Chyawanprash", category="Rejuvenative",
         dosha_effect="Tridoshic (adjust ratio for imbalance)", is_classical=True,
         typical_dose="1–2 tsp in warm milk",
         purpose="Immunity, respiratory, Rasayana (anti-aging), energy, Ojas building",
         cautions="Contains honey and sugar — adjust for diabetics (use sugar-free version)."),

    dict(name="Shilajit", name_sanskrit="Asphaltum punjabianum", category="Rejuvenative",
         dosha_effect="Reduces Kapha and Vata", is_classical=True,
         typical_dose="300–500 mg (resin: pea-sized)",
         purpose="Energy, testosterone, iron deficiency, anti-aging, brain, altitude sickness",
         cautions="Use purified Shilajit only. Raw form may contain heavy metals. Avoid with hyperthyroidism."),

    dict(name="Kanchanar Guggulu", name_sanskrit="Kanchanar + Guggulu compound", category="Thyroid/Lymph",
         dosha_effect="Reduces Kapha mainly", is_classical=True,
         typical_dose="2 tablets (250mg each) twice daily",
         purpose="Thyroid (hypothyroid, goiter, nodules), lymphatic, cysts, PCOS",
         cautions="Avoid in hyperthyroidism. Contains Guggulu — see Guggulu cautions."),

    dict(name="Avipattikar Churna", name_sanskrit="Avipattikar", category="Digestive",
         dosha_effect="Reduces Pitta", is_classical=True,
         typical_dose="1 tsp with water before meals",
         purpose="GERD, acidity, hyperacidity, gastric ulcers, Pitta digestion",
         cautions="Avoid in low Agni or Kapha-dominant conditions."),

    dict(name="Hingvastak Churna", name_sanskrit="Hingvastak", category="Digestive",
         dosha_effect="Reduces Vata, increases Pitta slightly", is_classical=True,
         typical_dose="1/2–1 tsp with warm water or ghee before meals",
         purpose="Gas, bloating, IBS, Vata digestion, abdominal cramping",
         cautions="Avoid with high Pitta, GERD, or ulcers."),

    dict(name="Sitopaladi Churna", name_sanskrit="Sitopaladi", category="Respiratory",
         dosha_effect="Reduces Vata, Pitta, and Kapha (Tridoshic for respiratory)", is_classical=True,
         typical_dose="1/2–1 tsp with honey",
         purpose="Cough, cold, bronchitis, fever, loss of appetite",
         cautions="Generally safe. Sweet in taste. May increase Kapha if overused."),

    dict(name="Talisadi Churna", name_sanskrit="Talisadi", category="Respiratory",
         dosha_effect="Reduces Vata and Kapha", is_classical=True,
         typical_dose="1/2–1 tsp with honey",
         purpose="Asthma, chronic cough, bronchitis, sinusitis, anorexia",
         cautions="Avoid in high Pitta conditions."),

    dict(name="Saraswatarishta", name_sanskrit="Saraswatarishta", category="Nervine",
         dosha_effect="Reduces Vata", is_classical=True,
         typical_dose="15–20 ml with equal water after meals",
         purpose="Memory, anxiety, epilepsy, speech disorders, mental clarity",
         cautions="Contains self-generated alcohol. Avoid with alcohol sensitivity or liver disease."),

    dict(name="Chandraprabha Vati", name_sanskrit="Chandraprabha Vati", category="Urinary/Metabolic",
         dosha_effect="Reduces all doshas", is_classical=True,
         typical_dose="2 tablets twice daily",
         purpose="Urinary disorders, diabetes, kidney stones, PCOS, hormonal balance",
         cautions="Avoid with renal failure (contains iron). Consult practitioner."),

    dict(name="Mahatriphala Ghrita", name_sanskrit="Mahatriphala Ghrita", category="Eye Health",
         dosha_effect="Reduces Pitta and Vata", is_classical=True,
         typical_dose="1 tsp on empty stomach",
         purpose="Eye health (glaucoma, cataracts, macular degeneration), brain tonic",
         cautions="Contains ghee — use with caution in high cholesterol or Kapha imbalance."),

    dict(name="Dashamoolarishta", name_sanskrit="Dashamoolarishta", category="Vata-pacifying",
         dosha_effect="Reduces Vata strongly", is_classical=True,
         typical_dose="15–20 ml with equal water after meals",
         purpose="Postpartum recovery, weakness, neurological support, joint pain",
         cautions="Contains self-generated alcohol. Avoid in pregnancy."),

    dict(name="Vasarishta", name_sanskrit="Vasarishta", category="Respiratory",
         dosha_effect="Reduces Kapha and Pitta", is_classical=True,
         typical_dose="15–20 ml after meals",
         purpose="Chronic respiratory disease, asthma, hemoptysis, TB support",
         cautions="Contains self-generated alcohol."),

    dict(name="Kutajarishta", name_sanskrit="Kutajarishta", category="Digestive",
         dosha_effect="Reduces Pitta and Kapha", is_classical=True,
         typical_dose="15–20 ml after meals",
         purpose="IBS, chronic diarrhea, dysentery, colitis, intestinal infections",
         cautions="Contains self-generated alcohol."),

    dict(name="Bhringraj", name_sanskrit="Eclipta alba", category="Hair/Liver",
         dosha_effect="Reduces Vata and Pitta", is_classical=True,
         typical_dose="500 mg – 1g or as hair oil",
         purpose="Hair loss, premature greying, liver support, skin, memory",
         cautions="Generally safe. Avoid high doses in pregnancy."),

    dict(name="Kumari (Aloe Vera)", name_sanskrit="Aloe barbadensis", category="Digestive/Skin",
         dosha_effect="Reduces Pitta mainly, mild Vata and Kapha", is_classical=True,
         typical_dose="1–2 oz fresh juice or 500 mg extract",
         purpose="Gut healing, GERD, skin, hormonal balance, liver",
         cautions="Laxative in high doses. Avoid latex portion if sensitive."),

    dict(name="Karela (Bitter Melon)", name_sanskrit="Momordica charantia", category="Metabolic",
         dosha_effect="Reduces Kapha and Pitta", is_classical=True,
         typical_dose="1–2 oz fresh juice or 500 mg extract",
         purpose="Blood sugar regulation, diabetes, liver, skin, antimicrobial",
         cautions="Monitor blood sugar closely if on insulin or diabetes medications."),

    dict(name="Methi (Fenugreek)", name_sanskrit="Trigonella foenum-graecum", category="Metabolic",
         dosha_effect="Reduces Kapha and Vata, may increase Pitta", is_classical=True,
         typical_dose="1 tsp seeds soaked overnight or 500 mg extract",
         purpose="Blood sugar, cholesterol, digestion, lactation, testosterone",
         cautions="May lower blood sugar — adjust diabetes medications. Avoid in pregnancy (stimulates uterus)."),

    dict(name="Coriander (Dhanyaka)", name_sanskrit="Coriandrum sativum", category="Digestive",
         dosha_effect="Reduces Pitta and Kapha", is_classical=True,
         typical_dose="1 tsp seeds in hot water (CCF tea) or in cooking",
         purpose="Digestion, burning sensation, UTI support, detox, cooling",
         cautions="Generally safe as food/tea."),

    dict(name="Cumin (Jiraka)", name_sanskrit="Cuminum cyminum", category="Digestive",
         dosha_effect="Reduces all doshas when used appropriately", is_classical=True,
         typical_dose="1 tsp seeds in hot water (CCF tea) or in cooking",
         purpose="Digestive fire, gas, bloating, iron absorption",
         cautions="Generally safe."),

    dict(name="Fennel (Shatapushpa)", name_sanskrit="Foeniculum vulgare", category="Digestive",
         dosha_effect="Reduces Vata and Pitta, neutral for Kapha", is_classical=True,
         typical_dose="1 tsp seeds in hot water (CCF tea) or chewed after meals",
         purpose="Gas, bloating, IBS, menstrual cramps, breast milk production",
         cautions="Estrogenic in high doses. Avoid high doses in estrogen-sensitive conditions."),

    dict(name="Ginger (Shunthi)", name_sanskrit="Zingiber officinale", category="Digestive",
         dosha_effect="Reduces Vata and Kapha, increases Pitta (use cautiously)", is_classical=True,
         typical_dose="1/4–1/2 tsp dry or 1-inch fresh",
         purpose="Nausea, digestion, inflammation, circulation, cold/flu",
         cautions="Avoid in high Pitta, GERD, or ulcers. Limit in pregnancy to small culinary doses."),

    dict(name="Cinnamon (Twak)", name_sanskrit="Cinnamomum verum", category="Metabolic",
         dosha_effect="Reduces Kapha and Vata, increases Pitta", is_classical=True,
         typical_dose="1/4–1/2 tsp daily",
         purpose="Blood sugar, circulation, digestion, antimicrobial",
         cautions="Use Ceylon cinnamon (not cassia). Avoid high doses in pregnancy."),

    dict(name="Cardamom (Ela)", name_sanskrit="Elettaria cardamomum", category="Digestive",
         dosha_effect="Reduces Vata and Kapha, neutral Pitta", is_classical=True,
         typical_dose="2–3 pods or 1/4 tsp ground",
         purpose="Digestion, breath, nausea, mucus, respiratory",
         cautions="Generally safe in culinary doses."),

    dict(name="Clove (Lavanga)", name_sanskrit="Syzygium aromaticum", category="Digestive",
         dosha_effect="Reduces Kapha and Vata, increases Pitta", is_classical=True,
         typical_dose="1–2 buds or small pinch powdered",
         purpose="Dental pain, digestion, antimicrobial, nausea",
         cautions="Avoid excessive doses. Clove oil is very potent."),

    dict(name="Black Pepper (Maricha)", name_sanskrit="Piper nigrum", category="Digestive",
         dosha_effect="Reduces Kapha and Vata, increases Pitta", is_classical=True,
         typical_dose="Pinch to 1/4 tsp",
         purpose="Bioavailability enhancer (curcumin, etc.), digestion, respiratory, anti-microbial",
         cautions="Avoid in high Pitta, GERD, or ulcers."),

    dict(name="Pippali (Long Pepper)", name_sanskrit="Piper longum", category="Respiratory",
         dosha_effect="Reduces Kapha and Vata, increases Pitta", is_classical=True,
         typical_dose="250–500 mg",
         purpose="Respiratory, Agni-kindling, bioavailability enhancer, liver",
         cautions="More potent than black pepper. Avoid with high Pitta."),

    dict(name="Kalonji (Nigella sativa)", name_sanskrit="Nigella sativa", category="Immunomodulator",
         dosha_effect="Reduces Kapha and Vata", is_classical=True,
         typical_dose="1/4–1/2 tsp seeds or 500 mg",
         purpose="Immunity, asthma, inflammation, blood sugar, anti-histamine",
         cautions="Avoid with blood thinners in high doses."),

    dict(name="Moringa (Shigru)", name_sanskrit="Moringa oleifera", category="Nutritive",
         dosha_effect="Reduces Kapha and Vata", is_classical=True,
         typical_dose="1 tsp powder or 500 mg",
         purpose="Iron deficiency, energy, thyroid support, anti-inflammatory, bone health",
         cautions="Avoid high doses in pregnancy (may cause contractions). Contains natural thyroid-stimulating compounds."),

    dict(name="Holy Basil (Tulsi)", name_sanskrit="Ocimum sanctum", category="Adaptogenic",
         dosha_effect="Reduces Vata and Kapha, neutral Pitta in normal doses", is_classical=True,
         typical_dose="1–2 tsp fresh leaves or tea",
         purpose="Adaptogen, stress, immunity, respiratory, antimicrobial, blood sugar",
         cautions="Mild blood thinner — avoid before surgery. Avoid high doses in pregnancy."),

    dict(name="Giloy Satva", name_sanskrit="Tinospora cordifolia extract", category="Immunomodulator",
         dosha_effect="Tridoshic", is_classical=True,
         typical_dose="500 mg once or twice daily",
         purpose="Concentrated Guduchi — fever, immunity, autoimmune support, liver",
         cautions="Same as Guduchi. May lower blood sugar."),
]

# ── Recipes ───────────────────────────────────────────────────────────────────

RECIPES = [
    dict(name="CCF Tea (Cumin-Coriander-Fennel)", meal_type="Drink", is_tea=True,
         dosha_good_for="Vata, Pitta, Kapha",
         ingredients="1 tsp cumin seeds, 1 tsp coriander seeds, 1 tsp fennel seeds, 2 cups water",
         instructions="Boil seeds in water for 5 minutes. Strain, sip warm throughout the day.",
         notes="The Ayurvedic gold standard for digestive tea. Kindles Agni, reduces bloating, flushes Ama."),

    dict(name="Golden Milk (Haldi Doodh)", meal_type="Drink", is_tea=False,
         dosha_good_for="Vata, Pitta", dosha_avoid="Kapha (reduce milk)",
         ingredients="1 cup warm whole milk (or almond milk), 1/2 tsp turmeric, 1/4 tsp cinnamon, pinch black pepper, 1 tsp ghee, honey to taste",
         instructions="Warm milk gently. Whisk in turmeric, cinnamon, black pepper and ghee. Add honey after removing from heat.",
         notes="Anti-inflammatory nightcap. Black pepper activates curcumin absorption by 2000%. Take before bed."),

    dict(name="Kitchari (Tridoshic)", meal_type="Lunch",
         dosha_good_for="Vata, Pitta, Kapha",
         ingredients="1/2 cup split mung dal, 1/2 cup basmati rice, 1 tbsp ghee, 1 tsp cumin seeds, 1/2 tsp turmeric, 1/2 tsp coriander, 1/4 tsp ginger, salt, 4 cups water",
         instructions="Rinse dal and rice. Sauté spices in ghee. Add dal, rice, water and turmeric. Cook on low 30-40 minutes until soft and porridge-like.",
         notes="The ultimate Ayurvedic cleanse food. Easy to digest, nourishing, balances all doshas. Use during illness or detox."),

    dict(name="Vata-Pacifying Oatmeal", meal_type="Breakfast",
         dosha_good_for="Vata", dosha_avoid="Kapha (reduce milk/sweetener)",
         ingredients="1/2 cup steel-cut oats, 1 cup whole milk or almond milk, 1/4 tsp cinnamon, 1/4 tsp cardamom, pinch nutmeg, 1 tsp ghee, dates or raisins",
         instructions="Cook oats in milk with spices. Top with ghee, dates, and a pinch of nutmeg.",
         notes="Warm, oily, sweet — perfectly Vata-pacifying. Eat warm, never cold oatmeal."),

    dict(name="Mung Dal Soup", meal_type="Dinner",
         dosha_good_for="Vata, Pitta, Kapha",
         ingredients="1 cup whole mung beans (soaked overnight), 1 tbsp ghee, 1 tsp cumin, 1/2 tsp turmeric, 1/2 tsp coriander, 1/4 tsp ginger, lime juice, cilantro, salt",
         instructions="Cook soaked mung until soft. Bloom spices in ghee (tadka). Combine, simmer 10 minutes. Finish with lime and cilantro.",
         notes="Lighter than kitchari. Excellent for detox, protein, and easy digestion. Best as light dinner."),

    dict(name="Kapha-Reducing Spiced Vegetable Soup", meal_type="Lunch",
         dosha_good_for="Kapha", dosha_avoid="Vata (add more ghee/oil)",
         ingredients="Mixed vegetables (cabbage, broccoli, carrots, celery), 1 tsp ginger, 1 tsp mustard seeds, 1/2 tsp turmeric, 1/4 tsp cayenne, black pepper, lemon, minimal oil",
         instructions="Lightly sauté mustard seeds in minimal oil. Add vegetables and spices. Add water, simmer 20 minutes. Finish with lemon.",
         notes="Light, pungent, dry qualities counter Kapha. Avoid heavy oils, cream, or butter."),

    dict(name="Pitta-Cooling Coconut Rice", meal_type="Lunch",
         dosha_good_for="Pitta", dosha_avoid="Kapha",
         ingredients="1 cup basmati rice, 1/2 cup coconut milk, 1 tsp ghee, 1/2 tsp cumin, fresh cilantro, lime, salt",
         instructions="Cook rice with coconut milk and water (half-half). Bloom cumin in ghee, add to rice. Top with cilantro and lime.",
         notes="Cooling, sweet, light. Perfect for hot summer days or high Pitta conditions."),

    dict(name="Ashwagandha Moon Milk", meal_type="Drink", is_tea=False,
         dosha_good_for="Vata", dosha_avoid="Kapha (reduce milk)",
         ingredients="1 cup warm milk, 1/2 tsp ashwagandha powder, 1/4 tsp cinnamon, pinch cardamom, pinch nutmeg, 1 tsp honey, 1 tsp ghee",
         instructions="Warm milk. Whisk in ashwagandha and spices. Add ghee. Sweeten with honey after cooling slightly.",
         notes="Deep sleep tonic. Builds Ojas and strength. Take 30-60 minutes before bed."),

    dict(name="Ginger Lemon Detox Drink", meal_type="Drink", is_tea=True,
         dosha_good_for="Kapha, Vata", dosha_avoid="Pitta (reduce ginger)",
         ingredients="1-inch fresh ginger (sliced), 1/2 lemon (juiced), 1 cup hot water, pinch of cayenne (optional), honey",
         instructions="Steep ginger in hot water 5-10 minutes. Add lemon and honey. Optional: pinch cayenne.",
         notes="Morning Agni-kindler. Flushes Ama, supports metabolism. Best taken 30 minutes before breakfast."),

    dict(name="Stewed Apples (Breakfast)", meal_type="Breakfast",
         dosha_good_for="Vata, Pitta",
         ingredients="2 apples (peeled, sliced), 1/4 tsp cinnamon, 1/4 tsp cardamom, pinch clove, 1/4 cup water, 1 tsp ghee",
         instructions="Cook apples with spices and water over medium heat until soft (10-15 minutes). Stir in ghee.",
         notes="Easiest Ayurvedic breakfast. Easy to digest, builds Ojas, gentle on gut. Perfect for detox days."),

    dict(name="Tulsi-Ginger Immunity Tea", meal_type="Drink", is_tea=True,
         dosha_good_for="Vata, Kapha", dosha_avoid="High Pitta",
         ingredients="5-6 fresh tulsi leaves (or 1 tsp dried), 3-4 slices fresh ginger, 1 tsp honey, 1 cup water",
         instructions="Boil water. Add tulsi and ginger, steep 5-7 minutes. Strain, cool slightly, add honey.",
         notes="Immunity powerhouse. Ideal during cold/flu season or monsoon. Antimicrobial, adaptogenic."),

    dict(name="Saffron Kheer (Rice Pudding)", meal_type="Snack",
         dosha_good_for="Vata, Pitta",
         ingredients="1/4 cup basmati rice, 2 cups whole milk, 1/4 tsp saffron (soaked in warm milk), 2 tbsp raw sugar or dates, 1/4 tsp cardamom, slivered almonds",
         instructions="Cook rice in milk on low heat until creamy (30-40 min), stirring frequently. Add saffron milk, sweetener, cardamom. Top with almonds.",
         notes="Nourishing Ojas-building dessert. Saffron is deeply healing for reproductive system and mood. Best for Vata and Pitta types."),

    dict(name="Chyawanprash Morning Shot", meal_type="Breakfast",
         dosha_good_for="Vata, Pitta, Kapha",
         ingredients="1-2 tsp Chyawanprash, 1 cup warm milk or water",
         instructions="Eat Chyawanprash directly or stir into warm milk. Take on empty stomach or with breakfast.",
         notes="Classical Rasayana (rejuvenative). 40+ herbs. Greatest Ayurvedic immunity tonic. Daily use recommended."),

    dict(name="Triphala Nighttime Tonic", meal_type="Drink", is_tea=False,
         dosha_good_for="Vata, Pitta, Kapha",
         ingredients="1/2–1 tsp Triphala churna, 1 cup warm water",
         instructions="Stir Triphala into warm (not hot) water. Drink 30-60 minutes before bed.",
         notes="Gentle bowel regulator, colon cleanser, eye health tonic. Best taken before bed. Consistency over 3+ months yields profound results."),

    dict(name="Vata-Soothing Dal with Ghee Tadka", meal_type="Dinner",
         dosha_good_for="Vata",
         ingredients="1 cup yellow toor dal, 2 tbsp ghee, 1 tsp cumin seeds, 1 tsp mustard seeds, 1/4 tsp asafoetida (hing), 1/2 tsp turmeric, 1/2 tsp ginger, salt, cilantro",
         instructions="Cook dal until very soft. Prepare tadka: heat ghee, pop mustard and cumin, add hing and ginger. Pour over dal. Garnish with cilantro.",
         notes="Ghee is essential for Vata. Rich, unctuous, warm. The hing and ginger prevent gas from the dal."),
]


# ── Seed function ─────────────────────────────────────────────────────────────

async def seed():
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(Supplement).limit(1))
        if result.scalars().first():
            print("Supplements already seeded — skipping.")
        else:
            supplements = [Supplement(**s) for s in SUPPLEMENTS]
            session.add_all(supplements)
            print(f"Inserted {len(supplements)} supplements.")

        result = await session.execute(select(Recipe).limit(1))
        if result.scalars().first():
            print("Recipes already seeded — skipping.")
        else:
            recipes = [Recipe(**r) for r in RECIPES]
            session.add_all(recipes)
            print(f"Inserted {len(recipes)} recipes.")

        await session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
