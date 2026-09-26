import sqlite3

def upgrade_ayurveda_patient_fields():
    conn = sqlite3.connect('aiia_app.db')
    c = conn.cursor()
    c.execute('PRAGMA table_info(ayur_patients)')
    cols = [col[1] for col in c.fetchall()]

    new_fields = [
        ('prakriti', 'Vata-Pitta'),
        ('vikriti', 'Pitta-Kapha Dushti'),
        ('agni', 'Vishama Agni (विषामाग्नि)'),
        ('koshtha', 'Madhyama Koshtha (मध्यम)'),
        ('diet_pathya', 'Yava (Barley), Karela, Mudga Yusha'),
        ('lifestyle_vihara', 'Pratahkala Vihara, Pranayama 20m'),
        ('anupana', 'Ushnodaka (Luke-warm Water)'),
        ('ayurvedic_history', 'Chronic Madhumeha (Vataja type), diagnosed 4 years prior')
    ]

    for col_name, default_val in new_fields:
        if col_name not in cols:
            c.execute(f'ALTER TABLE ayur_patients ADD COLUMN {col_name} TEXT DEFAULT "{default_val}"')

    # Add diverse data for specific patients
    c.execute("""
        UPDATE ayur_patients
        SET prakriti = 'Vata-Pitta',
            vikriti = 'Pitta Vriddhi (Pittaja Rashes)',
            agni = 'Vishama Agni',
            koshtha = 'Madhyama Koshtha',
            diet_pathya = 'Laghu, Tikta-Kashaya Rasa (Karela, Methi, Mudga)',
            lifestyle_vihara = 'Pranayama (Anulom-Vilom), avoid Divasvapna (daytime sleep)',
            anupana = 'Ushnodaka (Luke-warm Water)',
            ayurvedic_history = 'Madhumeha (Type 2 DM) with recent Twak Dushti'
        WHERE patient_id = 'AYU-PAT-001'
    """)

    c.execute("""
        UPDATE ayur_patients
        SET prakriti = 'Kapha-Vata',
            vikriti = 'Kapha Medo Dushti',
            agni = 'Manda Agni',
            koshtha = 'Krura Koshtha',
            diet_pathya = 'Yava, Kulattha, Shunthi Siddha Jala',
            lifestyle_vihara = 'Brisk walking 45m, Yoga Asanas (Surya Namaskar)',
            anupana = 'Koshna Jala (Warm water) with Madhu (Honey)',
            ayurvedic_history = 'Sthaulya (Obesity) and Aamavata'
        WHERE patient_id = 'AYU-PAT-002'
    """)

    conn.commit()
    conn.close()
    print("✓ Successfully enriched ayur_patients with comprehensive Ayurvedic parameters!")

if __name__ == '__main__':
    upgrade_ayurveda_patient_fields()
