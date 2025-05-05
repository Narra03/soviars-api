import psycopg2
from flask import Flask, request, render_template

app = Flask(__name__)

# Municipality list
municipalities = [
    "Adjuntas", "Aguada", "Aguadilla", "Aguas Buenas", "Aibonito", "Anasco", "Arecibo", "Arroyo",
    "Barceloneta", "Barranquitas", "Bayamon", "Cabo Rojo", "Caguas", "Camuy", "Canovanas",
    "Carolina", "Catano", "Cayey", "Ceiba", "Ciales", "Cidra", "Coamo", "Comerio", "Corozal",
    "Culebra", "Dorado", "Fajardo", "Florida", "Guanica", "Guayama", "Guayanilla", "Guaynabo",
    "Gurabo", "Hatillo", "Hormigueros", "Humacao", "Isabela", "Jayuya", "Juana Diaz", "Juncos",
    "Lajas", "Lares", "Las Marias", "Las Piedras", "Loiza", "Luquillo", "Manati", "Maricao",
    "Maunabo", "Mayaguez", "Moca", "Morovis", "Naguabo", "Naranjito", "Orocovis", "Patillas",
    "Penuelas", "Ponce", "Quebradillas", "Rincon", "Rio Grande", "Sabana Grande", "Salinas",
    "San German", "San Juan", "San Lorenzo", "San Sebastian", "Santa Isabel", "Toa Alta",
    "Toa Baja", "Trujillo Alto", "Utuado", "Vega Alta", "Vega Baja", "Vieques", "Villalba",
    "Yabucoa", "Yauco"
]

# Index mapping
INDEX_ALIASES = {
    'sovi': 'sovi_index',
    'vrs': 'vrs_index',
    'soviars': 'soviars_index',
    'readiness': 'readiness_index'
}

# Parse question to extract municipality and index type
def parse_question(question):
    question = question.lower()
    index_type = None
    mun = None

    for key in INDEX_ALIASES:
        if key in question:
            index_type = INDEX_ALIASES[key]
            break

    for m in municipalities:
        if m.lower() in question:
            mun = m
            break

    return mun, index_type

# Fetch value from PostgreSQL
def get_index_value(municipality, index_type):
    try:
        conn = psycopg2.connect(
            dbname='soviars',
            user='postgres',
            password='Sanjay@2001',  # Replace with your actual password
            host='localhost',
            port='5432'
        )
        cur = conn.cursor()
        query = f"SELECT {index_type} FROM indices WHERE LOWER(municipality) ILIKE LOWER(%s);"
        cur.execute(query, (f"%{municipality}%",))
        result = cur.fetchone()
        conn.close()

        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        return f"Error: {str(e)}"

# Main route
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')
@app.route('/ask', methods=['GET'])
def ask_question():
    question = request.args.get('q')
    municipality, index_type = parse_question(question)

    print("Parsed values →", municipality, index_type)

    if not municipality or not index_type:
        return "Sorry, I couldn't understand your question."

    result = get_index_value(municipality, index_type)

    if result is None:
        return "No data found for your request."

    try:
        value = float(result)
        return f"The {index_type.replace('_', ' ').title()} of {municipality} is {value:.2f}."
    except:
        return f"Something went wrong: {result}"

# Start the app
if __name__ == '__main__':
    app.run(debug=True)
