from flask import Flask, request, jsonify, render_template
import redis

# Conexión a Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Función para agregar una nueva receta
@app.route('/recetas', methods=['POST'])
def agregar_receta():
    data = request.get_json()
    nombre = data.get('nombre')
    ingredientes = data.get('ingredientes')
    pasos = data.get('pasos')

    nueva_receta = {
        'nombre': nombre,
        'ingredientes': ingredientes,
        'pasos': pasos
    }

    redis_client.hmset(f"receta:{nombre}", nueva_receta)
    return jsonify({"message": "Receta agregada con éxito."}), 201

# Función para actualizar una receta existente
@app.route('/recetas/<nombre>', methods=['PUT'])
def actualizar_receta(nombre):
    receta = redis_client.hgetall(f"receta:{nombre}")

    if receta:
        data = request.get_json()
        ingredientes = data.get('ingredientes')
        pasos = data.get('pasos')

        nueva_receta = {
            'nombre': nombre,
            'ingredientes': ingredientes,
            'pasos': pasos
        }

        redis_client.hmset(f"receta:{nombre}", nueva_receta)
        return jsonify({"message": "Receta actualizada con éxito."}), 200
    else:
        return jsonify({"message": "Receta no encontrada."}), 404

# Función para eliminar una receta existente
@app.route('/recetas/<nombre>', methods=['DELETE'])
def eliminar_receta(nombre):
    if redis_client.exists(f"receta:{nombre}"):
        redis_client.delete(f"receta:{nombre}")
        return jsonify({"message": "Receta eliminada con éxito."}), 200
    else:
        return jsonify({"message": "Receta no encontrada."}), 404

# Función para ver un listado de recetas
@app.route('/recetas', methods=['GET'])
def ver_listado_recetas():
    recetas = redis_client.keys("receta:*")
    listado = []

    if recetas:
        for receta_key in recetas:
            receta = redis_client.hgetall(receta_key)
            listado.append({
                "nombre": receta[b'nombre'].decode(),
                "ingredientes": receta[b'ingredientes'].decode().split(','),
                "pasos": receta[b'pasos'].decode()
            })
    else:
        return jsonify({"message": "No hay recetas en el libro."}), 404

    return jsonify(listado), 200

if __name__ == "__main__":
    app.run(debug=True)
