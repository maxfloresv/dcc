#include <bits/stdc++.h>
#include <iostream>
#include <fstream>
#include <typeinfo>
using namespace std;	
vector <vector <int>> adj;
vector <string> lines;
vector <int> blocks, identations;

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

// start: índice de inicio de lectura
// end: índice de fin de lectura
int build(int start, int end) {
	int line_size = (int) lines.size();
	// No podemos leer más líneas
	if (start >= line_size)
		return start-1;
	
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
				adj[i].push_back(s-1);
				return s-1;
			}
			
			int out = build(i+1, s-1);
			
			// Conectamos el nodo actual con el siguiente
			adj[i].push_back(i+1);
			// Conectamos ambos a la salida (si encontramos un
			// else, la borramos de adj[i] posteriormente)
			adj[i].push_back(out);
			adj[i+1].push_back(out);
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
				adj[i].push_back(s-1);
				return s-1;
			}

			int d = i;
			while (--d >= 0 && identations[i] < identations[d])
				continue;
				
			// Nos entrega la salida del if inmediatamente anterior
			int out = build(d, s-1);
			auto itr = find(adj[d].begin(), adj[d].end(), out);
			
			// Si el iterador existe, lo borramos
			if (itr != adj[d].end())
				adj[d].erase(itr);
				
			// Agregamos la condición del else
			adj[d].push_back(i+1);
			adj[i+1].push_back(out);
			
			build(i+1, s-1);
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
				adj[i].push_back(s-1);
				return s-1;
			}

			int out = build(i+1, s-1);
			// Conectamos el while con el cuerpo y la salida
			adj[i].push_back(i+1);
			adj[i].push_back(out);
			// Conectamos el último bloque con el while
			// TO-DO: Hay que determinar el último bloque,
			// no necesariamente es i+1
			adj[i+1].push_back(i);
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
				
			if (!ok) {
				// Si no se pudo conectar a código, conectamos al
				// nodo que apunta a "FIN"
				adj[i].push_back(s-1);
				return s-1;
			}

			// Tengo que conectar con el nodo "FIN"
			if (s == line_size)
				adj[i].push_back(i+1);
			else
				// Sino, sigue habiendo código y conecto con la salida
				adj[i].push_back(build(i+1, s-1));
		}
	}
	
	// Retornamos el nodo de salida. 
	// s viene inmediatamente después de end.	
	return s;
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
			
			// Luego, eliminamos las tabulaciones
			replace(line.begin(), line.end(), '\t', '\0');
			lines.push_back(line);
			
			line = line.substr(identations[i]); // cagada de maximo hace bien la wea
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
		
		lines.push_back("fin");
		blocks.push_back(++indexBlocks); 
		// Consideraremos que esta línea no tiene identación
		identations.push_back(0);
	}
	
	for (int i=0;i<(int)blocks.size(); i++)
		cout << "linea: " << lines[i] << " / bloque: " << blocks[i] << " / identacion: " << identations[i] << '\n';
	
	// TO-DO:: llamar a las funciones que generen las aristas
	// y hacer el dfs
	int len = blocks[blocks.end()];
	cout<<len<<endl;
	adj.resize(len);
	build(0, len-1);
	for (int i=0; i<(int) adj.size(); i++) {
		cout << "i = " << i << '\n';
		for (int j=0; j<(int) adj[i].size(); j++) {
			cout << adj[i][j] << ' ';
		}
		cout << '\n';
	}
	
	return 0;
}
