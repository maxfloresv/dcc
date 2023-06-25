#include <bits/stdc++.h>
#include <iostream>
#include <fstream>
#include <typeinfo>
using namespace std;
using state = pair <int, int>;
// Usamos un vector de sets para que no se repitan índices
vector <set <int>> adj;
vector <string> lines;
vector <int> blocks, identations;
// Para el DFS y para las líneas visitadas
vector <bool> visited;
// Mapa de variables con las líneas para revisar error
// TO-DO: set <state>. (L, 0) indica definición y (L, 1) indica uso
map <char, set <int>> vars; 
// Almacena la información de cada while
map <state, vector <int>> node_to_while;

// Encontrar el lower bound (estrictamente menor) del set s
int get_lower_bound(set <int> s, int bound) {
	int m = -1;
	for (int i : s) {
		if (i < bound)
			m = i;
	}
	return m;
}

bool is_valid_char(char s) {
	// Uso de la tabla ASCII para determinar si tengo una
	// variable o no (https://www.ascii-code.com/)
	return 'a' <= s && s <= 'z';
}

// Revisa si los primeros caracteres de s son iguales a comp
bool match(string s, string comp) {
	int len = (int) comp.size();
	return s.substr(0, len) == comp;
}

int indentation(string s, int num_chars = 1) {
	int id = 0;
	// Construimos el string con las tabulaciones rastreadas
	string t(num_chars, '\t');

	// Buscamos hasta que ya no existan coincidencias
	if (match(s, t)) {
		id++;
		id += indentation(s, num_chars + 1);
	}

	return id;
}

void var_detector(string s, int line) {
	int size = (int) s.size();
	// Asumiendo buena sintaxis, este caso es imposible, pero
	// es importante handlearlo por si acaso
	if (size == 1)
		return;

	if (!is_valid_char(s[1]))
		vars[s[0]].insert(blocks[line]);

	for (int i=1; i<size-1; i++) {
		// El caso s[i+1] == '(' es porque es función. Ej: f(x, y)
		if (!is_valid_char(s[i]) || s[i+1] == '(')
			continue;

		if (!is_valid_char(s[i-1]) && !is_valid_char(s[i+1]))
			vars[s[i]].insert(blocks[line]);
	}
}

void dfs(int s) {
    stack <int> pila;                  
    pila.push(s);

    while (!pila.empty()) {
        int u = pila.top();
        pila.pop();
        
        visited[u] = true;

        for (int v: adj[u]) {
            if (!visited[v]) {
				// TO-DO: agregar dfs modificado
				visited[v] = true;
				pila.push(v);
            }
        }
    }
}

// start := línea de inicio del while
// end := última línea del while
// tab := la tabulación del while
// Devuelve res := un vector con los bloques que se conectan con el while padre
vector <int> conectar_while(int start, int end, int tab) {
	// whiles := Número de las líneas cuya identación sea menor a la ultima linea 
	// del while padre.
	vector <int> whiles, res;
	int t = identations[end];
	// t2 es una copia para comparar
	int t2 = t;
	int i = end, j = end;

	// Mientras hayan tabulaciones mayores a tab. Termina cuando llegamos
	// a la tabulación del while padre, porque ahí se cumple t2 == tab.
	// Marca los cambios de tabulación de abajo hacia arriba.
	while (t2 > tab) {
		t = identations[i];
		// Arregla el problema de la identificación de bloque de los else dentro del while
		if (match(lines[i], "else") && get_lower_bound(adj[blocks[i-1]], blocks[i-1]) == -1) {
			whiles.push_back(i-1);
			t2--;
		}

		// Se ejecuta cuando encontramos la primera tabulación menor
		else if (t2 == t) {
			whiles.push_back(i);
			t2--;
		}
		i--;
	}

	int whiles_size = (int) whiles.size();
	// Encuentra el while con menor identación. Si no existe el end queda igual.
	for (int k = whiles_size - 1; k >= 0; k--) {
		// Revisamos en orden de menor a mayor identación si alguna línea donde
		// cambia la identación empieza un while.
		if (match(lines[whiles[k]], "while")) {
			end = whiles[k];
			break;
		}
	}

	// -- Hallar los bloques que retornan al while padre --
	if (end == j)
		// Caso 1: No había while. j siempre es código sin keywords.
		for (int k = 0; k < whiles_size; k++)
			res.push_back(blocks[whiles[k]]);

	else {
		// Caso 2: Había while
		int k = (int) whiles.size() - 1;
		// Agrega todas las líneas que están estrictamente arriba del while
		// sólo si tienen una identación menor
		while (whiles[k] <= end) {
			res.push_back(blocks[whiles[k]]);
			k--;
		}
	}

	return res;
}

int contar_arcos() {
	int adj_sz = (int) adj.size();
	int ans = 0;
	for (int i = 0; i < adj_sz; i++)
		ans += adj[i].size();
	
	return ans;
}

// start: índice de inicio de lectura
// end: índice de fin de lectura
// Crea las aristas del grafo
void build(int start, int end, bool inside_while) {
	int line_size = (int) lines.size(), end_while = -1;
	vector <int> res;
	// No podemos leer más líneas
	if (start >= line_size || start > end)
		return;
	
	int s = start;
	for (int i = start; i < end; i++) {
		// Array de la línea actual
		string line = lines[i];
		// Actualizamos s como el índice de la instrucción actual
		s = i;
		bool ok = 1;
		if (match(line, "if")) {
			// Caso if
			while (++s < line_size && identations[i] < identations[s]) {
				// Estoy en la última iteración posible
				if (s == line_size-1)
					// Entonces no hubo ninguna línea que cumplió
					// la condición identations[i] < identations[s]
					ok = 0;
					
				continue;
			}
			
			if (!ok && !inside_while) {
				// Si no se pudo conectar a código, conectamos al
				// nodo que apunta a "FIN"
				adj[blocks[i]].insert(blocks[s-1]);
				return;
			}
			
			// Conectamos el nodo actual con el siguiente
			// i+1 es la línea siguiente al if
			adj[blocks[i]].insert(blocks[i+1]);

			// Conectamos ambos a la salida (si encontramos un
			// else, la borramos de adj[blocks[i]] posteriormente)
			// Lo ejecutamos sólo si no estamos dentro de un while
			if (!inside_while) {
				adj[blocks[i]].insert(blocks[s]);
				if (!match(lines[s], "else")) {
					// Quitar aristas si habian ifs de por medio
					if (adj[blocks[i]].size() > 2)
						for (int j : adj[blocks[i]])
							if (j > blocks[s])
								adj[blocks[i]].erase(j);
				}
			}
			
			// La llamada recursiva para analizar el bloque
			// que está entremedio
			build(i+1, s-1, inside_while);
		}

		else if (match(line, "else")) {
			while (++s < line_size && identations[i] < identations[s]) {
				if (s == line_size-1)
					ok = 0;
					
				continue;
			}

			if (!ok && !inside_while) {
				adj[blocks[i+1]].insert(blocks[s-1]);
				return;
			}

			int d = i, iden = identations[d-1];
			bool else_visited = false, in_while = false;
			while (0 <= --d && identations[i] < identations[d]) {
				auto prev_itr = find(adj[blocks[d]].begin(), adj[blocks[d]].end(), blocks[i-1]);
				auto itr = find(adj[blocks[d]].begin(), adj[blocks[d]].end(), blocks[i+1]);
				// Si se encontro el while cambiar variable a false
				if (match(lines[d], "while"))
					in_while = false;

				// Resetear variable cuando terminamos de usarla
				else if (match(lines[d], "if"))
					else_visited = false;

				// Cambiar estado de variable cuando corresponde
				else if (match(lines[d], "else"))
					else_visited = true;

				// Verificar si la linea esta dentro de un while
				if (get_lower_bound(adj[blocks[d]], blocks[d]) != -1)
					in_while = true;

				// Cambiar solo si no estoy dentro de while o la línea siguiente es un else
				if (!in_while || match(lines[d+1], "else")) {
					// Caso se conectan a linea anterior al else
					if (prev_itr != adj[blocks[d]].end()) {
						if (!match(lines[d], "if") && !match(lines[d], "else") && !match(lines[d], "while")) {
							adj[blocks[d]].erase(*prev_itr);
							adj[blocks[d]].insert(blocks[s]);
						}

						else if (match(lines[d], "if") && adj[blocks[d]].size() > 2) {
							adj[blocks[d]].erase(*prev_itr);
							adj[blocks[d]].insert(blocks[d+1]);
						}
					}

					// Revisar si existe algo que borrar
					if (itr != adj[blocks[d]].end()) {
						adj[blocks[d]].erase(*itr);
						adj[blocks[d]].insert(blocks[s]);
					}
					// Caso else dentro del if correspondiente al else
					else if (match(lines[d+1], "else") && !else_visited && identations[i-1] != identations[i+1]) {
						adj[blocks[d]].insert(blocks[s]);
						else_visited = true;
					}
				}
			}

			// Agregamos la conexión con lo que sigue sólo si
			// no está dentro de un while
			if (!inside_while)
				adj[blocks[i+1]].insert(blocks[s]);
			
			build(i+1, s-1, inside_while);
		}

		else if (match(line, "while")) {
			// Caso while
			while (++s < line_size && identations[i] < identations[s]) {
				if (s == line_size-1)
					ok = 0;
					
				continue;
			}
			
			if (!ok && !inside_while) {
				adj[blocks[i]].insert(blocks[s-1]);
				return;
			}

			// Conectamos el while con el cuerpo y la salida
			adj[blocks[i]].insert(blocks[i+1]);
			adj[blocks[i]].insert(blocks[s]);

			// Conectamos los bloques correspondientes con el while
			res = conectar_while(i+1, s-1, identations[i]);
			// Asociamos el bloque del while con su vector res
			node_to_while[{blocks[i], s}] = res;

			for (int j = 0; j < (int) res.size(); j++)
				adj[res[j]].insert(blocks[i]);
			
			build(i+1, s-1, true);
			end_while = s;
			inside_while = false;
		}

		else {
			// Caso de código sin keywords. Tiene que ser <= porque no
			// necesariamente hay sólo una línea de código sin keywords.
			while (++s < line_size && identations[i] < identations[s]) {
				if (s == line_size-1)
					ok = 0;
					
				continue;
			}
			
			if (!ok && !inside_while) {
				adj[blocks[i]].insert(blocks[s-1]);
				return;
			}

			// Tengo que conectar con el nodo "FIN"
			if (s == line_size && !inside_while)
				adj[blocks[i]].insert(blocks[i+1]);

			else if (!inside_while) 
				adj[blocks[i]].insert(blocks[s]);
			
			build(i+1, s-1, inside_while);
		}
	}
}

int main() {
	fstream file;
	// ios::in para leer el archivo
	file.open("prueba.txt", ios::in);
	
	if (file.is_open()) {
		string line;
		// Procesamos el archivo y los bloques
		int i = 0, indexBlocks = 0, last_id = -1;
		while (getline(file, line)) {
			// Primero vemos las identaciones
			int id_line = indentation(line);
			// Las agregamos a un vector
			identations.push_back(id_line);
			
			// Luego, empezamos desde el primer caracter válido
			line = line.substr(identations[i]);
			lines.push_back(line);
			
			// Revisa si la línea actual empieza con una instrucción
			if (match(line, "if")) {
				// Si la linea anterior tiene distinta tabulación
				if (last_id != id_line){
					// caso if o else previo a un if
					if (i > 0 && !match(lines[i-1], "else") && !match(lines[i-1], "if") && !match(lines[i-1], "while"))
						indexBlocks++;
				}
				
				blocks.push_back(indexBlocks);
				indexBlocks++;
			}
			else if (match(line, "else")) {
				indexBlocks++;
				blocks.push_back(indexBlocks);
			}
			else if (match(line, "while")) {
				// Si la linea anterior no tiene condición
				if (i > 0 && !match(lines[i-1], "while") && !match(lines[i-1], "else") && !match(lines[i-1], "if"))
					indexBlocks++;

				blocks.push_back(indexBlocks);
				indexBlocks++;
			}
			else {
				if (last_id > id_line)
					indexBlocks++;
				blocks.push_back(indexBlocks);
			}
			i++;
			last_id = id_line;
		}
		
		file.close();
		
		lines.push_back("FIN");
		blocks.push_back(++indexBlocks); 
		// Consideraremos que esta línea no tiene identación
		identations.push_back(0);
	}

	// Corremos el detector de variables. Notemos que las líneas
	// están 0-indexadas
	int current = 0;
	for (string line : lines) {
		if (line == "FIN")
			continue;

		var_detector(line, current++);
	}

	// imprime linea de texto / bloque / identacion, razones de "debugging"
	for (int i=0;i<(int)lines.size(); i++)
		cout << "linea: " << lines[i] << " / bloque: " << blocks[i] << " / identacion: " << identations[i] << '\n';
	
	//TODO:: hacer el dfs
	int blocks_sz = (int) blocks.size();
	// Entrega el número de nodos y arcos
	int nodos = blocks[blocks_sz-1];
	// Agregamos el nodo final
	nodos++;

	adj.resize(nodos);
	visited.assign(nodos, false);
	build(0, blocks_sz-1, false);

	for (auto itr = node_to_while.begin(); itr != node_to_while.end(); itr++) {
		state key = itr->first;
		auto [block, out] = key;

		cout << "{" << block << ", " << out << "}: ";
		for (int v : node_to_while[key]) {
			cout << v << ' ';
			// Nos entrega el iterador (o .end()) que indica si algún bloque
			// conectado al while padre está conectado a la salida de dicho while
			auto ady = find(adj[v].begin(), adj[v].end(), blocks[out]);

			// Si el iterador existe, borramos la arista porque no deberían ir a out
			if (ady != adj[v].end())
				adj[v].erase(*ady);

			// Inserta las aristas que falta que se devuelvan al while padre
			adj[v].insert(block);
		}
		cout << '\n';
	}

	// Borramos la "diagonal"
    for (int i = 0; i < nodos; i++)
        for (int j : adj[i])
            if (j == i) {
                adj[i].erase(i);
				break;
			}

	int arcos = contar_arcos();
	// Imprime el mapa vars
	cout << "-----MAPA-----\n";
	for (auto itr = vars.begin(); itr != vars.end(); itr++) {
		char key = itr->first;
		set <int> s = vars[key];
		cout << key << ": ";
		for (int j : s) 
			cout << j << ' ';
		cout << '\n';
	}
	
	cout << "-----LISTA DE ADYACENCIA-----\n";
	for (int i = 0; i < nodos; i++) {
		cout << i << ": ";
		for (int j : adj[i])
			cout << j << ' ';
		cout << '\n';
	}
	
	cout << "CFG\n";
	cout << "Nodos: " << nodos << '\n';
	cout << "Arcos: " << arcos << '\n';
	cout << "Componentes conexos: 1\n\n";
	
	cout << "Variables indefinidas\n";
	cout << "Variable: \n";
	cout << "Camino: \n\n";
	
	cout << "Complejidad ciclomática\n";
	cout << arcos - nodos + 2 << "\n";
	
	return 0;
}