#include <bits/stdc++.h>
#include <iostream>
#include <fstream>
#include <typeinfo>
using namespace std;	
vector <vector <int>> adj;
vector <string> lines;
vector <int> blocks, identations;

// ok
bool is_valid_char(char s) {
	// Uso de la tabla ASCII para determinar si tengo una
	// variable o no (https://www.ascii-code.com/)
	return 'a' <= s && s <= 'z';
}

// ok
char* string_to_array(string s) {
	int len = (int) s.size();
	
	// Se le suma 1 por el caracter nulo al final
	char* res = new char[len + 1];
	strcpy(res, s.c_str());
	
	return res;
}

// ok
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


void padre(int s) {
	return;
}

// start: índice de inicio de lectura
void build(int start) {
	int line_size = (int) lines.size();
	if (start >= line_size)
		return;
	
	for (int i=start; i<line_size; i++) {
		
	}
	// Estamos en un caso donde el índice i es if sin else
	
	// Caso base if solo
	if (if) {
		adj[i].push_back(i+1);
		// Solo conectamos si existe código después
		if (i+2 < line_size) {
			adj[i].push_back(i+2);
			adj[i+1].push_back(i+2);
		}
		build(i+1);
	}
	
	else if (if else) {
		adj[i].push_back(i+1);
		adj[i].push_back(i+2);
		// Ídem
		if (i + 3 < line_size) {
			adj[i+1].push_back(i+3);
			adj[i+2].push_back(i+3);
		}
		build(i+1);
	} 
	
	else if (while) {
		
	} 
	
	else {
		// i es puro código
		if (i >= 1)
			adj[i].push_back(padre(i-1))
	}
		
	// Caso base while solo
	} else if (
		
	check_if(...)
}*/

// main() ok
int main() {
	fstream file;
	// ios::in para leer el archivo
	file.open("prueba.txt", ios::in);
	
	if (file.is_open()) {
		string line;
		// Procesamos el archivo y los bloques
		int i = 0, indexBlocks = 1, last_id = -1;
		while (getline(file, line)) {
			// Primero vemos las identaciones
			int id_line = identation(line, "", 1);
			// Las agregamos a un vector
			identations.push_back(id_line);
				
			// Luego, eliminamos las tabulaciones
			replace(line.begin(), line.end(), '\t', '\0');
			lines.push_back(line);
			
			char* line_ = string_to_array(line);
			// Revisa si la línea actual empieza con una instrucción
			if (!strncmp("if", line_, 2)) {
				blocks.push_back(indexBlocks);
				indexBlocks++;
			}
			else if (!strncmp("else", line_, 4)) {
				blocks.push_back(indexBlocks);
				indexBlocks++;
			}
			else if (!strncmp("while", line_, 5)) {
				// Si la linea anterior no tiene while
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
	
	// TO-DO:: llamar a las funciones que generen las aristas
	// y hacer el dfs
	// build(0)
	
	return 0;
}
