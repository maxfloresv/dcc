#include <bits/stdc++.h>
#include <iostream>
#include <fstream>
#include <typeinfo>
using namespace std;
// Usamos un vector de sets para que no se repitan índices
vector <set <int>> adj;
vector <string> lines;
vector <int> blocks, identations;
// Para el DFS
vector <bool> visited;
// Mapa de variables con las líneas para revisar error
map <char, vector <int>> vars; 

bool is_valid_char(char s) {
	// Uso de la tabla ASCII para determinar si tengo una
	// variable o no (https://www.ascii-code.com/)
	return 'a' <= s && s <= 'z';
}

char* string_to_array(string s) {
	int len = (int) s.size();
	
	// Se le suma 1 por el caracter nulo al final
	char* res = new char[len + 1];
	strcpy(res, s.c_str());

	return res;
}

int identation(string s, string tp, int tab) {
	int id = 0;
	tp += "\t";
	char* s_ = string_to_array(s);
	char* tp_ = string_to_array(tp);
	if (!strncmp(tp_, s_, tab)) {
		id++;
		id += identation(s, tp, tab+1);
	}
	return id;
}

bool check_first(string inst, char* arr) {
	int len = (int) inst.size();
	char* inst_ = string_to_array(inst);
	return !strncmp(inst_, arr, len);
}

void dfs(int s) {
    stack <int> pila;                  
    pila.push(s);

    while (!pila.empty()) {
        int u = pila.top();
        pila.pop();
        
        visited[u] = true;

        for (int v: adj[u]) {
            if (visited[v] == 0) {
				// TO-DO: agregar dfs modificado
                visited[v] = 1;
                pila.push(v);
            }
        }
    }
}

vector <int> conectar_while(int start, int end, int tab) {
	// numero de la linea donde esta cada while con identacion menor a la ultima linea
	vector <int> whiles, res;
	int t = identation(lines[end], "", 1), t2 = t;
	int i = end, j = end;
	
	// mientras hayan tabulaciones mayores a tab (la tabulacion del while que estamos comprobando actualmente)
	while (t2 > tab) {
		t = identation(lines[i], "", 1);
		if (t2 == t) 
			whiles.push_back(i);
		t2--;
		i--;
	}

	// encontrar el while con menor identacion
	// si no existe el end queda igual
	for (int i=0; i<whiles.size(); i++) {
		if (check_first(lines[whiles[i]], "while")){
			end = whiles[i];
			break;
		}
	}

	// hallar los bloques que retornan al while padre
	// Caso no habia while
	if (end == j){
		for (int i=0; i<whiles.size(); i++)
			res.push_back(blocks[i]);
	}

	// Caso habia while
	else {
		int k = whiles.size();
		while (whiles[k] != end) {
			res.push_back(blocks[whiles[k]]);
			k--;
		}
		res.push_back(blocks[whiles[k]]);
	}

	//TODO Caso else

	return res;
}

int contar_arcos() {
	int adj_sz = (int) adj.size();
	int ans = 0;
	for (int i=0; i<adj_sz; i++)
		ans += adj[i].size();
	
	return ans;
}

// start: índice de inicio de lectura
// end: índice de fin de lectura
// Crea las aristas del grafo
void build(int start, int end, bool inside_while) {
	int line_size = (int) lines.size();
	// No podemos leer más líneas
	if (start >= line_size || start > end)
		return;
	
	int s = start;
	for (int i=start; i<end; i++) {
		// Array de la línea actual
		char* line = string_to_array(lines[i]);
		// Actualizamos s como el índice de la instrucción actual
		s = i;
		bool ok = 1;
		
		if (check_first("if", line)) {
			// i+1 es la línea siguiente al if
			while (++s < line_size && identations[i] < identations[s]) {
				// Estoy en la última iteración posible
				if (s == line_size-1 && identations[i] < identations[s])
					// Entonces no hubo ninguna línea que cumplió
					// la condición iden[i] < iden[s]
					ok = 0;
					
				continue;
			}
			
			if (!ok) {
				// Si no se pudo conectar a código, conectamos al
				// nodo que apunta a "FIN"
				adj[blocks[i]].insert(blocks[s-1]);
				return;
			}
			
			// Conectamos el nodo actual con el siguiente
			adj[blocks[i]].insert(blocks[i+1]);
			// Conectamos ambos a la salida (si encontramos un
			// else, la borramos de adj[blocks[i]] posteriormente)
			// Lo hacemos sólo si no estamos dentro de un while
			if (!inside_while) {
				adj[blocks[i]].insert(blocks[s]);
				adj[blocks[i+1]].insert(blocks[s]);
			}
			
			// La llamada recursiva para analizar el bloque
			// que está entremedio
			build(i+1, s-1, inside_while);
		}
		else if (check_first("else", line)) {
			while (++s < line_size && identations[i] < identations[s]) {
				// Estoy en la última iteración posible
				if (s == line_size-1 && identations[i] < identations[s])
					// Entonces no hubo ninguna línea que cumplió
					// la condición iden[i] < iden[s]
					ok = 0;
					
				continue;
			}
				
			if (!ok) {
				// Si no se pudo conectar a código, conectamos al
				// nodo que apunta a "FIN"
				adj[blocks[i+1]].insert(blocks[s-1]);
				return;
			}

			int d = i;
			while (--d >= 0 && identations[i] < identations[d])
				continue;
				
			// Nos entrega la salida del if inmediatamente anterior
			//int out = build(d, s-1);
			set <int> curr = adj[blocks[d]];
			auto itr = find(curr.begin(), curr.end(), blocks[s]);
			
			// Si el iterador existe, lo borramos
			if (itr != curr.end())
				curr.erase(itr);
				
			// Agregamos la condición del else
			curr.insert(blocks[i+1]);
			// Agregamos la conexión con lo que sigue sólo si
			// no está dentro de un while
			if (!inside_while)
				adj[blocks[i+1]].insert(blocks[s]);
			
			// Revisamos recursivamente el bloque que está dentro
			build(i+1, s-1, inside_while);
		}
		else if (check_first("while", line)) {
			while (++s < line_size && identations[i] < identations[s]) {
				// Estoy en la última iteración posible
				if (s == line_size-1 && identations[i] < identations[s])
					// Entonces no hubo ninguna línea que cumplió
					// la condición iden[i] < iden[s]
					ok = 0;
					
				continue;
			}
			
			if (!ok) {
				// Si no se pudo conectar a código, conectamos al
				// nodo que apunta a "FIN"
				adj[blocks[i]].insert(blocks[s-1]);
				return;
			}

			// Conectamos el while con el cuerpo y la salida
			adj[blocks[i]].insert(blocks[i+1]);
			adj[blocks[i]].insert(blocks[s]);
			// Conectamos los bloques correspondientes con el while 
			vector <int> res = conectar_while(i+1, s-1, identations[i]);
			for (int j=0; j<res.size(); j++) {
				adj[res[j]].insert(blocks[i]);
			}
			
			build(i+1, s-1, true);
			inside_while = false;
		}
		else {
			// Caso de código sin keywords
			while (++s < line_size && identations[i] < identations[s]) {
				// Estoy en la última iteración posible
				if (s == line_size-1 && identations[i] < identations[s])
					// Entonces no hubo ninguna línea que cumplió
					// la condición iden[i] < iden[s]
					ok = 0;
					
				continue;
			}
				
			if (!ok && !inside_while) {
				// Si no se pudo conectar a código, conectamos al
				// nodo que apunta a "FIN"
				adj[blocks[i]].insert(blocks[s-1]);
				return;
			}

			// Tengo que conectar con el nodo "FIN"
			if (s == line_size && !inside_while)
				adj[blocks[i]].insert(blocks[i+1]);
			else if (!inside_while) {
				// Sino, sigue habiendo código y conecto con la salida
				adj[blocks[i]].insert(blocks[s]);
			}
			
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
			int id_line = identation(line, "", 1);
			// Las agregamos a un vector
			identations.push_back(id_line);
			
			// Luego, empezamos desde el primer caracter válido
			line = line.substr(identations[i]);
			lines.push_back(line);
			
			char* line_ = string_to_array(line);
			// Revisa si la línea actual empieza con una instrucción
			if (check_first("if", line_)) {
				blocks.push_back(indexBlocks);
				indexBlocks++;
			}
			else if (check_first("else", line_)) {
				blocks.push_back(indexBlocks);
				indexBlocks++;
			}
			else if (check_first("while", line_)) {
				// Si la linea anterior no tiene condición
				if (last_id == id_line)
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
	
	for (int i=0;i<(int)lines.size(); i++)
		cout << "linea: " << lines[i] << " / bloque: " << blocks[i] << " / identacion: " << identations[i] << '\n';
	
	// TO-DO:: llamar a las funciones que generen las aristas
	// y hacer el dfs
	int blocks_sz = (int) blocks.size();
	// Entrega el número de nodos y arcos
	int nodos = blocks[blocks_sz-1];

	adj.resize(nodos);
	visited.assign(nodos, false);
	build(0, nodos-1, false);

	int arcos = contar_arcos();
	
	for (int i=0; i<nodos; i++) {
		cout << "i = " << i << '\n';
		for (auto j=adj[i].begin(); j != adj[i].end(); j++){
			cout << *j << ' ';
		}
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
	cout << arcos - nodos + 2;
	
	return 0;
}
