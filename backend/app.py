from flask import Flask, jsonify, request, send_from_directory, session
import json
import re
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

import os
app.secret_key = os.environ.get("ZUFATECH_SECRET_KEY", "change-this-secret-before-deployment")

@app.route("/images/<path:filename>")
def product_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
LANDING_DIR = PROJECT_DIR / "landing"
DATABASE = BASE_DIR.parent.parent / "shop.db"
IMAGE_DIR = BASE_DIR.parent.parent


#  the 44 product cards in the existing ZUFATECH LIMITED index.html.
# Prices are the KSh amounts shown in each card's price text.
PRODUCT_SEED = [{'id': 1,
  'name': 'Apple iPad Pro 12.9 (2020) 12.9"',
  'description': 'WI-FI 128GB 256GB 512GB 1TB iPadOS 13.4 9720mAh',
  'image': 'AppleIpad12pro.jpg',
  'prices': [114000],
  'active': True},
 {'id': 2,
  'name': 'SamSung Galaxy S24Ultra',
  'description': '• Display: 6.78" QHD+ flat AMOLED, 120Hz refresh rate\n'
                 '         • Processor: Snapdragon 8 Gen 3\n'
                 '         • Rear Camera: 200MP + 12MP + 50MP + 10MP\n'
                 '         • Front Camera: 12MP selfie\n'
                 '         • Battery & Charging: 5000mAh with 45W fast charging\n'
                 '         • Build & Memory: Titanium frame, LPDDR5X RAM, UFS 4.0 storage',
  'image': 'GalaxyS24Ultra.jpg',
  'prices': [107000],
  'active': True},
 {'id': 3,
  'name': 'SamsungGalaxyS26',
  'description': '• Display: 6.9″ QHD+ 120Hz LTPO AMOLED with Privacy Display mode Avechi Kenya.\n'
                 '           • Processor: Snapdragon 8 Elite Gen 5 (3nm) Avechi Kenya.\n'
                 '           • Cameras: 200MP (f/1.4 main) + 50MP + 10MP + 50MP rear / 12MP selfie Avechi '
                 'Kenya.\n'
                 '           • Battery: 5000mAh with upgraded 60W wired charging.\n'
                 '           • Build: Aluminum frame with built-in S Pen.',
  'image': 'GalaxyS26 Ultra.jpg',
  'prices': [180000, 140600, 126000],
  'active': True},
 {'id': 4,
  'name': 'GalaxyZFold5',
  'description': '• Main Screen: 7.6" 120Hz Dynamic AMOLED (2176 x 1812)\n'
                 '           • Cover Screen: 6.2" 120Hz Dynamic AMOLED (2316 x 904)\n'
                 '           • Processor: Snapdragon 8 Gen 2 for Galaxy\n'
                 '           • Memory: 12GB RAM | 256GB / 512GB / 1TB storage\n'
                 '           • Rear Cameras: 50MP Main (OIS) + 12MP Ultra-wide + 10MP Telephoto (3x zoom)\n'
                 '           • Front Cameras: 10MP (Cover) + 4MP (Under-display main)\n'
                 '           • Battery: 4,400 mAh | 25W wired | 15W wireless\n'
                 '           • Durability: IPX8 water resistance | 253 grams',
  'image': 'GalaxyZFold5.jpg',
  'prices': [130000, 79000],
  'active': True},
 {'id': 5,
  'name': 'GalaxyZFold6',
  'description': '• Main Screen: 7.6" 120Hz Dynamic AMOLED (2160 x 1856, 2600 nits)\n'
                 '           • Cover Screen: 6.3" 120Hz Dynamic AMOLED (2376 x 968)\n'
                 '           • Processor: Snapdragon 8 Gen 3 for Galaxy\n'
                 '           • Memory: 12GB RAM | 256GB / 512GB / 1TB storage\n'
                 '           • Rear Cameras: 50MP Main (OIS) + 12MP Ultra-wide + 10MP Telephoto (3x zoom)\n'
                 '           • Front Cameras: 10MP (Cover) + 4MP (Under-display main)\n'
                 '           • Battery: 4,400 mAh | 25W wired | 15W wireless\n'
                 '           • Durability: IP48 dust and water resistance | 239 grams',
  'image': 'GalaxyZFold6.jpg',
  'prices': [137000, 147500],
  'active': True},
 {'id': 6,
  'name': 'HUAWEI NOVA10',
  'description': '• Performance: Snapdragon 778G 4G processor.\n'
                 '           • Display: 6.67-inch Curved 120Hz OLED screen.\n'
                 '           • Camera System: 60MP Front Camera + 50MP Triple Rear Setup.\n'
                 '           • Battery Ecosystem: 4,000 mAh battery supporting 66W fast charging.',
  'image': 'Huawei Nova10.jpg',
  'prices': [54000, 73000],
  'active': True},
 {'id': 7,
  'name': 'Huawei P50 pocket',
  'description': '• Dual Displays: Features a large 6.9-inch foldable 120Hz OLED main screen paired with a '
                 'circular 1.04-inch cover screen for quick notifications.\n'
                 '           • Performance: Powered by the flagship Snapdragon 888 4G processor, combined '
                 'with 8GB or 12GB of RAM.\n'
                 '           • Unique Camera: Equipped with a 40MP + 13MP + 32MP Ultra Spectrum triple '
                 'camera setup that can be used for high-quality selfies when folded.\n'
                 '           • Battery & Charging: Packs a 4,000 mAh battery that supports 40W Huawei '
                 'SuperCharge wired fast charging.',
  'image': 'HuaweiP50Ppocket.jpg',
  'prices': [168000, 113000],
  'active': True},
 {'id': 8,
  'name': 'HUAWEI PURAX MAX',
  'description': '• Massive Dual Displays: Opens up into a giant 7.7-inch foldable 120Hz LTPO2 OLED main '
                 'screen, with a tough 5.4-inch outer cover screen.\n'
                 '           • Flagship Kirin Performance: Powered by the advanced Kirin 9030 Pro (6nm) '
                 'processor paired with up to 16GB of RAM.\n'
                 '           • Huge Battery Capacity: Features a massive 5,300 mAh battery that supports '
                 'both 66W wired and 50W wireless fast charging.',
  'image': 'HuaweiPuraX.jpg',
  'prices': [205000, 228000, 245000],
  'active': True},
 {'id': 9,
  'name': 'Apple Iphone 13 Pro',
  'description': '• Fluid Display: A premium 6.1-inch Super Retina XDR OLED screen with Apple’s 120Hz '
                 'ProMotion smooth refresh rate.\n'
                 '           • Pro Cameras: Triple 12MP camera array featuring 3x optical zoom, macro '
                 'photography, and a LiDAR scanner for low-light focusing.\n'
                 '           • Powerful Chipset: Powered by the flagship A15 Bionic chip with 6GB RAM, fully '
                 'supporting the latest iOS updates.\n'
                 '           • Premium Build: Made with a tough Ceramic Shield front and heavy '
                 'surgical-grade stainless steel borders.',
  'image': 'iphone13 pro.jpg',
  'prices': [46000, 60000],
  'active': True},
 {'id': 10,
  'name': 'Apple Iphone 16Pro',
  'description': '• Display: 6.3-inch 120Hz ProMotion OLED screen with Dynamic Island.\n'
                 '           • Processor: Flagship A18 Pro (3 nm) chip with 8GB RAM for Apple Intelligence.\n'
                 '           • Cameras: 48MP main, 48MP ultrawide, and 12MP telephoto with 5x optical zoom.\n'
                 '           • Hardware: Premium titanium frame featuring the dedicated Camera Control '
                 'button.',
  'image': 'iphone16pro.jpg',
  'prices': [112000, 150000],
  'active': True},
 {'id': 11,
  'name': 'Apple Iphone17 Pro',
  'description': '• A19 Pro & 12GB RAM: Powered by the flagship A19 Pro (3 nm) chip with a major memory bump '
                 'to 12GB RAM for advanced local AI tools.\n'
                 '           • Triple 48MP Cameras: Features an all-upgraded 48MP triple lens system (Main, '
                 'Ultrawide, and Telephoto) supporting a 4x optical zoom.\n'
                 '           • Anti-Reflective Screen: A 6.3-inch 120Hz ProMotion OLED display featuring a '
                 'sharper, anti-reflective coating and 3,000 nits peak brightness.\n'
                 '           • Cooler Hardware: Built inside a newly designed aluminum unibody shell using '
                 'an internal laser-welded vapor chamber for optimal cooling.',
  'image': 'iphone17pro.jpg',
  'prices': [153000, 191999, 220990],
  'active': True},
 {'id': 12,
  'name': 'Apple Iphone 18 Promax',
  'description': '• Variable Aperture Camera: Debuts a game-changing 48MP main lens with mechanical variable '
                 'aperture (ƒ/1.48 to ƒ/4.0), matched with dual 48MP ultrawide and periscope lenses.\n'
                 '           • 2nm A20 Pro Powerhouse: Driven by Apple’s next-generation A20 Pro (2 nm) chip '
                 'bundled with 12GB RAM, running on a more advanced vapor chamber cooling setup.\n'
                 '           • Stretched 6.9-Inch Display: Features a larger 6.9-inch LTPO OLED screen with '
                 'a 35% narrower Dynamic Island and an anti-reflective coating.\n'
                 '           • Massive Battery: Packs a substantial 5,391 mAh battery supporting 43 hours of '
                 'video playback—marking the longest runtime on any iPhone to date.',
  'image': 'iphone18promax.jpg',
  'prices': [219000, 245000, 320000],
  'active': True},
 {'id': 13,
  'name': 'Modio Kids Tablet',
  'description': 'Entertainment on the Move (SIM Supported): Equipped with built-in cellular SIM card slots '
                 '(4G/5G). Kids can stream or download educational content during travel without needing '
                 'Wi-Fi.',
  'image': 'KidsTablet2.jpg',
  'prices': [6000],
  'active': True},
 {'id': 14,
  'name': '7-Inch Android Educational Kids Tablet',
  'description': 'Ready for School & CBC Apps: Built on an open Android system with native access to the '
                 'Google Play Store, making it simple to download YouTube Kids, Google Classroom, and local '
                 'CBC curriculum tools.',
  'image': 'KidsTablet7.jpg',
  'prices': [7600],
  'active': True},
 {'id': 15,
  'name': 'Lenovo Tab Plus',
  'description': '• Integrated JBL 8-Speaker Sound: Houses a massive 8-speaker JBL audio system with Dolby '
                 'Atmos that can double entirely as a premium standalone Bluetooth speaker for your phone.\n'
                 '           • Built-in Metal Kickstand: Features a sturdy, built-in backside hinge that '
                 'opens up to 175 degrees, allowing you to easily prop the tablet up on any flat surface '
                 'without an extra case.\n'
                 '           • Sharp 2K 90Hz Screen: Equipped with a bright, crisp 11.5-inch 2K display '
                 'featuring a smooth 90Hz refresh rate and built-in eye-care certification.',
  'image': 'LenovoTablet.jpg',
  'prices': [56000],
  'active': True},
 {'id': 16,
  'name': 'Modio M129 Android Tablet',
  'description': 'Modio M129 Android Tablet is a highly versatile 8-inch device featuring dual-SIM 5G '
                 'connectivity, 8GB RAM, and a massive 512GB of internal storage bundled with a free '
                 'Bluetooth keyboard and wireless mouse, making it an exceptional, budget-friendly laptop '
                 'alternative uniquely suited for both school assignments and everyday business workflows.',
  'image': 'Modio M129Tablet.jpg',
  'prices': [10500],
  'active': True},
 {'id': 17,
  'name': 'Nokia 2 V Tella',
  'description': '5.45-inch HD+ display, a MediaTek Helio A22 processor, 2GB RAM, 16GB of expandable '
                 'storage, and a 3,000 mAh removable USB-C battery.',
  'image': 'Nokia2VTella.jpg',
  'prices': [9500],
  'active': True},
 {'id': 18,
  'name': 'Nokia G42 5G',
  'description': 'Nokia G42 5G So Grey 256GB + 8GB Dual-Sim Factory Unlocked GSM NEW',
  'image': 'NokiaG42.jpg',
  'prices': [117500],
  'active': True},
 {'id': 19,
  'name': 'NokiaPLight',
  'description': 'Coming Soon(stay tuned)',
  'image': 'NokiaPLight.jpg',
  'prices': [],
  'active': False},
 {'id': 20,
  'name': 'Nokia 106 (2018 version)',
  'description': '• Battery: 800 mAh removable cell offering up to 15.7 hours of talk time and 21 days of '
                 'standby power.\n'
                 '           • Storage & SIM: 4 MB internal memory holding 2,000 contacts alongside Dual '
                 'Mini-SIM slots for network flexibility.',
  'image': 'NokiaSmall1.jpg',
  'prices': [2000],
  'active': True},
 {'id': 21,
  'name': 'Nokia 150 (2023 version)',
  'description': '• Battery: 1450 mAh removable battery delivering up to 20 hours of talk time and up to 30 '
                 'days of standby.\n'
                 '           • SIM & Hardware: Equipped with Dual SIM slots, a 2.4-inch QVGA display, and a '
                 'VGA rear camera with an LED flash.',
  'image': 'NokiaSmall2.jpg',
  'prices': [2800],
  'active': True},
 {'id': 22,
  'name': 'Oraimo SpaceBox Active 25W Portable Wireless Speaker (Model: OBS-680).',
  'description': '• Audio Output: Packed with 25W powerful sound integrated with a HavyBass algorithm for '
                 'deep, punchy audio.\n'
                 '            • Battery Life: Provides up to 14 hours of continuous music playtime on a '
                 'single charge.\n'
                 '            • Durability: Features an IP55 dust and water resistance rating, making it '
                 'completely splashproof for outdoor use.',
  'image': 'Oraimo SpaceboxActive.jpg',
  'prices': [5000],
  'active': True},
 {'id': 23,
  'name': 'oraimo SpaceBuds Hybrid ANC True Wireless Earbuds (Model: OTW-630).',
  'description': '• Noise Cancellation: Equipped with up to 50dB Hybrid Active Noise Cancellation (ANC) and '
                 'a Smart Chat mode that automatically pauses music when you speak.\n'
                 '           • Battery Life: Delivers up to 40 hours of total playtime with the charging '
                 'case when ANC is turned off (11 hours from the buds alone).\n'
                 '           • Audio Quality: Driven by 11mm dynamic drivers combined with oraimo’s '
                 'signature HavyBass™ tuning for deeply enriched sound',
  'image': 'Oraimo SpaceBudsWireless.jpg',
  'prices': [5500],
  'active': True},
 {'id': 24,
  'name': 'Oraimo Slice Link 10000mAh Power Bank(Model: OPB-P5101)',
  'description': 'Cables: Built-in Type-C, Lightning, and Micro-USB cords.',
  'image': 'OraimoPortable Powerbank.jpg',
  'prices': [2599],
  'active': True},
 {'id': 25,
  'name': 'Oraimo Halo OEP-E21 Wired Headphones',
  'description': '• Audio Setup: Built with 10mm dynamic drivers optimized for heavy, punchy bass '
                 'performance and clear midrange audio.\n'
                 '            • Connectivity: Equipped with a standard 1.2-meter durable cable terminating '
                 'in a universal 3.5mm audio plug.\n'
                 '            • Control Unit: Outfitted with an in-line single microphone remote for easy '
                 'hands-free phone calls and continuous music playback tracking.',
  'image': 'OraimoWired Headphones.jpg',
  'prices': [500],
  'active': True},
 {'id': 26,
  'name': 'Picun F8 Pro Hybrid Active Noise Cancelling Headphones',
  'description': '• Active Noise Cancelling: Advanced -52dB Hybrid ANC filters out heavy background '
                 'environment sounds.\n'
                 '           • Extreme Battery Life: Delivers up to a class-leading 140 hours of continuous '
                 'music playback on one single charge cycle.\n'
                 '           • Immersive Technology: Supports built-in 3D spatial audio with head tracking '
                 'capability and weighs only 286 grams.',
  'image': 'PicusF5Wireless Bluetooth Headphones.jpg',
  'prices': [9800],
  'active': True},
 {'id': 27,
  'name': 'Xiaomi Redmi 17 (4G)',
  'description': '• Screen: Features  6.9-inch 120Hz IPS LCD panel.\n'
                 '           • Hardware: Runs a MediaTek Helio G91-Ultra chipset under Xiaomi HyperOS 3.\n'
                 '           • Battery: Packs a massive 7,500mAh capacity with 45W turbo charging.\n'
                 '           • Cameras: Outfitted with a 50MP primary rear sensor and an 8MP front lens.',
  'image': 'Redmi17.jpg',
  'prices': [19499, 24199, 28000],
  'active': True},
 {'id': 28,
  'name': 'Xiaomi Redmi Note 15 (4G)',
  'description': '• MediaTek Helio G100-Ultra processor, operating on Xiaomi HyperOS 2 built over Android '
                 '15.\n'
                 '            • Screen: Sports a vibrant 6.77-inch AMOLED display featuring an ultra-smooth '
                 '120Hz refresh rate and 3,200 nits peak brightness.\n'
                 '            • Imaging & Battery: Outfitted with a high-resolution 108MP super-clear '
                 'camera, a 20MP front lens, and a massive 6,000mAh battery with 33W fast charging.',
  'image': 'RedmiNote15.jpg',
  'prices': [26000, 28999],
  'active': True},
 {'id': 29,
  'name': 'Samsung GalaxyS22',
  'description': '• Snapdragon 8 Gen 1 (or Exynos 2200) chip alongside an integrated S-Pen slot.\n'
                 '            • Screen: Curved 6.8-inch Dynamic AMOLED 2X panel featuring an adaptive 120Hz '
                 'refresh rate.\n'
                 '            • Cameras: Pro-grade setup carrying a 108MP main camera with OIS, 10x '
                 'periscope telephoto lens, and a 40MP selfie shooter.\n'
                 '            • Endurance: Equipped with a 5,000mAh battery that supports 45W wired fast '
                 'charging and IP68 resistance.',
  'image': 'samsungGalaxyS22.jpg',
  'prices': [48960, 64899, 104999],
  'active': True},
 {'id': 30,
  'name': 'Samsung Galaxy S23Ultra',
  'description': '• Snapdragon 8 Gen 2 for Galaxy processor with an embedded S-Pen stylus.\n'
                 '             • Screen: 6.8-inch curved QHD+ Dynamic AMOLED 2X panel with an adaptive 120Hz '
                 'refresh rate.\n'
                 '             • Cameras: Elite quad setup featuring a flagship 200MP main lens with OIS, '
                 '10x periscope zoom, and a 12MP front sensor.\n'
                 '             • Endurance: Large 5,000mAh battery paired with 45W wired fast charging and '
                 'IP68 dust/water protection.',
  'image': 'SamsungGalaxyS23Ultra.jpg',
  'prices': [74000, 110500, 135000],
  'active': True},
 {'id': 31,
  'name': 'Samsung Galaxy S25 Ultra',
  'description': '• Snapdragon 8 Elite chip driving an anti-reflective 6.9-inch 120Hz Dynamic LTPO AMOLED 2X '
                 'flat display.\n'
                 '             • Cameras: Features a premium quad camera system headlined by a 200MP main '
                 'lens, alongside dedicated 50MP periscope (5x), 10MP telephoto (3x), and 50MP ultrawide '
                 'sensors.\n'
                 '             • Design & Power: Built with a durable Grade 5 Titanium frame housing an '
                 'integrated S-Pen, an IP68 water resistance rating, and a 5,000mAh battery with 45W fast '
                 'charging.',
  'image': 'SamsungGalaxyS25Ultra.jpg',
  'prices': [130500, 145000, 165000],
  'active': True},
 {'id': 32,
  'name': 'Samsung Galaxy S20 Ultra 5G',
  'description': '• Immersive Display: Sports a large 6.9-inch Dynamic AMOLED 2X screen supporting an '
                 'ultra-smooth 120Hz refresh rate.\n'
                 '           • High-Res Pro Cameras: Outfitted with an elite 108MP main rear quad-camera '
                 'system featuring 100x Space Zoom, paired with a sharp 40MP front selfie shooter.\n'
                 '           • Hardware & Battery: Powered by a high-performance octa-core processor bundled '
                 'with a heavy-duty 5,000mAh battery that supports 45W super fast charging.',
  'image': 'SamsungS20.jpg',
  'prices': [34000, 52000, 35000, 58000, 42000, 68000],
  'active': True},
 {'id': 33,
  'name': 'Teco Camon 20 Pro 4G',
  'description': '• Display Layout: Immersive 6.67-inch AMOLED screen with a smooth 120Hz refresh rate.\n'
                 '            • Camera System: High-resolution 64MP main rear camera setup paired with a '
                 'sharp 32MP front selfie lens.\n'
                 '            • Storage & Power: Packed with 256GB internal storage, 8GB RAM, and a '
                 'long-lasting 5,000mAh battery.',
  'image': 'TecnoCamon20.jpg',
  'prices': [24000],
  'active': True},
 {'id': 34,
  'name': 'Tecno Spark 20Pro',
  'description': '• Display Layout: Built with a 6.78-inch Curved AMOLED screen delivering an ultra-smooth '
                 '120Hz refresh rate.\n'
                 '           • Camera Array: Features a high-resolution 108MP main rear camera paired with a '
                 '32MP front selfie camera.\n'
                 '           • Core Processing: Powered by an octa-core MediaTek Helio G99 Ultimate chipset '
                 'coupled with 256GB storage and 8GB RAM',
  'image': 'TecnoSpark20Pro.jpg',
  'prices': [27999],
  'active': True},
 {'id': 35,
  'name': 'Tecno Spark 40 Pro',
  'description': '• Vibrant High-Speed Display: Built with a premium 6.78-inch 144Hz Flexible AMOLED panel '
                 'hitting an immersive 1224×2720 resolution for high-end smoothness.\n'
                 '            • Robust Daily Battery: Carries a reliable 5,200mAh battery that fuels long '
                 'user sessions and replenishes quickly with standard 45W fast charging.\n'
                 '            • Capable Processing Layout: Operates using a MediaTek Helio G100 Ultimate '
                 'silicon processor optimized for fluid task execution and casual gaming sessions.',
  'image': 'TecnoSpark40.jpg',
  'prices': [22000, 25500],
  'active': True},
 {'id': 36,
  'name': 'Tecno Spark50',
  'description': '• Flagship-Grade Durability:IP68 and IP69 dust and water resistance, protecting the phone '
                 'against continuous immersion and high-pressure hot water jets.\n'
                 '           • Vibrant High-Refresh Display:6.78-inch panel paired with an ultra-smooth '
                 '120Hz refresh rate for smooth scrolling and animations.\n'
                 '           • Massive Battery & Rapid Powering:5,600mAh battery designed for multi-day '
                 'endurance, recharging swiftly using integrated 60W Super Charging.\n'
                 '           • Optimized Everyday Performance: Powered by the reliable MediaTek Helio G100 '
                 'Ultimate chipset, it easily handles daily tasks and casual gaming.',
  'image': 'TecnoSpark50.jpg',
  'prices': [24000, 30000],
  'active': True},
 {'id': 37,
  'name': 'TYPE C CHARGER',
  'description': '• Wattage: 25W maximum power output per charging port.\n'
                 '           • Cable Length: 6 feet (~1.8 meters) each.\n'
                 '           • Port Type: Single USB Type-C interface on each block.',
  'image': 'TYPE C CHARGER.JPG',
  'prices': [1110],
  'active': True},
 {'id': 38,
  'name': 'Wired Headphones12xBarkstech',
  'description': '• Durable K-12 Audio Build: Heavy-duty, adjustable on-ear headphones feature easy-to-wipe '
                 'synthetic earpads for rapid classroom sanitation.\n'
                 '            • Tangle-Free School Connectivity: Tough 3.5ft flat cords prevent classroom '
                 'tangles and terminate in a universal 3.5mm jack for Chromebooks, tablets, and laptops.',
  'image': 'Wired Headphones12xBarkstech.jpg',
  'prices': [11680, 1170, 12980, 2000],
  'active': True},
 {'id': 39,
  'name': 'Xiaomi Redmi K100 Pro Max',
  'description': '• Snapdragon 8 Elite Gen 5 processing. It features a 6.9-inch 1.5K AMOLED screen. The '
                 'panel hits a 185Hz refresh rate and 10,000 nits brightness.\n'
                 '             • Power comes from a 9,070mAh Silicon-Carbon battery. It supports 100W wired '
                 'charging. It also supports 50W wireless charging.\n'
                 '             • The camera setup has a 200MP main lens with OIS. It adds 50MP telephoto and '
                 '8MP ultrawide sensors. A 32MP front camera handles selfies. The system operates on Xiaomi '
                 'HyperOS 3 with Android 16.',
  'image': 'Xiaomi RedmiK100 Pro.jpg',
  'prices': [87000],
  'active': True},
 {'id': 40,
  'name': 'Phone Case',
  'description': 'Protective and stylish phone cases.',
  'image': 'phone cases.jpg',
  'prices': [500],
  'active': True},
 {'id': 41,
  'name': '7.1 Channel Gaming Headset',
  'description': 'Immersive sound for gaming and music.',
  'image': '7.1Channel GamingHeadset.jpg',
  'prices': [2500],
  'active': True},
 {'id': 42,
  'name': 'Besundy Rugged Smartwatch',
  'description': 'Display: 1.81-inch HD touchscreen.',
  'image': 'Besundy.jpg',
  'prices': [2500, 3999],
  'active': True},
 {'id': 43,
  'name': 'Apple/Iphone Charger',
  'description': 'Best of our Orginal Charger',
  'image': 'AppleCharger.jpg',
  'prices': [500],
  'active': True},
 {'id': 44,
  'name': 'Screen Protector',
  'description': 'Help protect your screen from scratches.',
  'image': 'screen protector.jpg',
  'prices': [300],
  'active': True}]


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                image TEXT NOT NULL DEFAULT '',
                prices_json TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                total REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                unit_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Seed the database only when it has no products. This avoids overwriting
        # catalogue edits made later in the database.
        count = db.execute("SELECT COUNT(*) AS count FROM products").fetchone()["count"]
        if count == 0:
            db.executemany(
                "INSERT INTO products (id, name, description, image, prices_json, active) VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (p["id"], p["name"], p["description"], p["image"], json.dumps(p["prices"]), int(p["active"]))
                    for p in PRODUCT_SEED
                ]
            )


def product_json(row):
    prices = json.loads(row["prices_json"])
    return {
        "id": row["id"], "name": row["name"], "description": row["description"],
        "image": row["image"], "prices": prices, "active": bool(row["active"])
    }



@app.route("/")
def home():
    return send_from_directory(LANDING_DIR, "Index.html")



@app.route("/<path:filename>")
def website_files(filename):
    return send_from_directory(LANDING_DIR, filename)



@app.get("/api/products")
def get_products():
    with get_db() as db:
        rows = db.execute("SELECT * FROM products ORDER BY id").fetchall()
    return jsonify({"products": [product_json(row) for row in rows]})


@app.post("/api/orders")
def create_order():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Please submit order details."}), 400

    name = str(data.get("customer_name", "")).strip()
    email = str(data.get("email", "")).strip()
    phone = str(data.get("phone", "")).strip()
    items = data.get("items")

    if len(name) < 2:
        return jsonify({"error": "Enter your full name."}), 400
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"error": "Enter a valid email address."}), 400
    if not phone or len(phone) > 30:
        return jsonify({"error": "Enter a valid phone number."}), 400
    if not isinstance(items, list) or not items or len(items) > 100:
        return jsonify({"error": "Your cart must contain items."}), 400

    order_lines = []
    total = 0
    with get_db() as db:
        for item in items:
            if not isinstance(item, dict):
                return jsonify({"error": "Invalid cart item."}), 400
            product_id = item.get("product_id")
            price = item.get("price")
            quantity = item.get("quantity", 1)
            if isinstance(product_id, bool) or not isinstance(product_id, int):
                return jsonify({"error": "Invalid product."}), 400
            if isinstance(quantity, bool) or not isinstance(quantity, int) or not 1 <= quantity <= 100:
                return jsonify({"error": "Quantity must be between 1 and 100."}), 400
            row = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if row is None or not row["active"]:
                return jsonify({"error": "This product is unavailable."}), 400
            allowed_prices = json.loads(row["prices_json"])
            # The server checks the chosen price against the allowed price options.
            if isinstance(price, bool) or not isinstance(price, (int, float)) or price not in allowed_prices:
                return jsonify({"error": f"Invalid price selected for {row['name']}."}), 400
            subtotal = float(price) * quantity
            total += subtotal
            order_lines.append({
                "product_id": product_id, "name": row["name"], "price": float(price),
                "quantity": quantity, "subtotal": subtotal
            })

        cursor = db.execute(
    """
    INSERT INTO orders
        (customer_name, email, phone, total,items_json)
    VALUES (?, ?, ?, ?,?)
    """,
    (
        name,
        email,
        phone,
        total,
        json.dumps(order_lines)
    )
)
        order_id = cursor.lastrowid
        db.executemany(
            "INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
            [(order_id, line["product_id"], line["name"], line["price"], line["quantity"], line["subtotal"]) for line in order_lines]
        )

    return jsonify({"message": "Order saved successfully.", "order_id": order_id,
                    "total": total, "currency": "KES", "items": order_lines}), 201


@app.post("/api/contact")
def save_contact_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Please submit a contact message."}), 400
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    phone = str(data.get("phone", "")).strip()
    message = str(data.get("message", "")).strip()
    if len(name) < 2:
        return jsonify({"error": "Enter your full name."}), 400
    
        return jsonify({"error": "Enter a valid email address."}), 400
    if not phone or len(phone) > 30:
        return jsonify({"error": "Enter a valid phone number."}), 400
    if not message:
        return jsonify({"error": "Please enter a message."}), 400
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO contact_messages (customer_name, email, phone, message) VALUES (?, ?, ?, ?)",
            (name, email, phone, message)
        )
        message_id = cursor.lastrowid
    return jsonify({"message": "Your message was saved successfully.", "message_id": message_id}), 201


@app.get("/api/orders")
def list_orders():
    
    with get_db() as db:
        orders = db.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
        result = []
        for order in orders:
            lines = db.execute("SELECT product_name, unit_price, quantity, subtotal FROM order_items WHERE order_id = ?", (order["id"],)).fetchall()
            result.append({**dict(order), "items": [dict(line) for line in lines]})
    return jsonify({"orders": result})

from flask import session

@app.get("/api/admin/config-check")
def admin_config_check():
    return jsonify({
        "password_configured": bool(
            os.environ.get("ZUFATECH_ADMIN_PASSWORD")
        ),
        "username_configured": bool(
            os.environ.get("ZUFATECH_ADMIN_USERNAME")
        ),
        "secret_configured": bool(
            os.environ.get("ZUFATECH_SECRET_KEY")
        )
    })


@app.post("/api/admin/login")
def admin_login():
    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    admin_username = os.environ.get("ZUFATECH_ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ZUFATECH_ADMIN_PASSWORD")

    if not admin_password:
        return jsonify({
            "error": "Admin password is not configured on the server."
        }), 503

    if username != admin_username or password != admin_password:
        return jsonify({"error": "Incorrect username or password."}), 401

    session["is_admin"] = True
    return jsonify({"message": "Admin login successful."})


@app.post("/api/admin/logout")
def admin_logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})


def check_admin_login():
    if not session.get("is_admin"):
        return jsonify({"error": "Please log in as admin."}), 401
    return None


@app.get("/api/admin/products")
def admin_get_products():
    auth_error = check_admin_login()
    if auth_error:
        return auth_error

    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT id, name, description, image, prices_json, active "
            "FROM products ORDER BY id DESC"
        ).fetchall()

        products = []
        for row in rows:
            item = dict(row)
            item["prices"] = json.loads(item.pop("prices_json"))
            item["active"] = bool(item["active"])
            products.append(item)

        return jsonify({"products": products})
    finally:
        conn.close()


@app.post("/api/admin/products")
def admin_add_product():
    auth_error = check_admin_login()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Please submit product details."}), 400

    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()
    image = str(data.get("image", "")).strip()
    prices = data.get("prices")
    active = 1 if data.get("active", True) else 0

    if not name:
        return jsonify({"error": "Product name is required."}), 400

    if not isinstance(prices, list) or not prices:
        return jsonify({"error": "Enter at least one price."}), 400

    try:
        prices = [float(price) for price in prices]
    except (TypeError, ValueError):
        return jsonify({"error": "Prices must be valid numbers."}), 400

    if any(price <= 0 for price in prices):
        return jsonify({"error": "Prices must be greater than zero."}), 400

    conn = get_db()
    try:
        cursor = conn.execute(
            """
            INSERT INTO products
                (name, description, image, prices_json, active)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, description, image, json.dumps(prices), active),
        )
        conn.commit()
        return jsonify({
            "message": "Product added successfully.",
            "product_id": cursor.lastrowid
        }), 201
    finally:
        conn.close()


@app.put("/api/admin/products/<int:product_id>")
def admin_update_product(product_id):
    auth_error = check_admin_login()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Please submit product details."}), 400

    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()
    image = str(data.get("image", "")).strip()
    prices = data.get("prices")
    active = 1 if data.get("active", True) else 0

    if not name:
        return jsonify({"error": "Product name is required."}), 400

    if not isinstance(prices, list) or not prices:
        return jsonify({"error": "Enter at least one price."}), 400

    try:
        prices = [float(price) for price in prices]
    except (TypeError, ValueError):
        return jsonify({"error": "Prices must be valid numbers."}), 400

    if any(price <= 0 for price in prices):
        return jsonify({"error": "Prices must be greater than zero."}), 400

    conn = get_db()
    try:
        cursor = conn.execute(
            """
            UPDATE products
            SET name = ?, description = ?, image = ?,
                prices_json = ?, active = ?
            WHERE id = ?
            """,
            (
                name, description, image,
                json.dumps(prices), active, product_id
            ),
        )

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"error": "Product not found."}), 404

        conn.commit()
        return jsonify({"message": "Product updated successfully."})
    finally:
        conn.close()



init_db()

if __name__ == "__main__":
    app.run(debug=True)



