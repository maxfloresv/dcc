#include <bits/stdc++.h>
#include <iostream>
#include <fstream>
#include <typeinfo>
using namespace std;

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

int main() {
	fstream file;
	// ios::in para leer el archivo
	file.open("prueba.txt", ios::in);
	
	// Este mapa almacena cada variable usada y su estado.
	// false := No tiene problema. true := Generó un error.
	map <char, bool> used_vars;
	map <char, vector <bool>> graph;
	vector <string> inst;
	
	// Cada while agregará una cantidad de nodos distintas. El que
	// tiene código agrega 3, y el que no, agrega 2.
	// NC := no tiene código antes (un tipo de while)
	int while_nc_cnt = 0;
	// C := sí tiene código (otro tipo de while)
	int while_c_cnt = 0;
	int if_cnt = 0;
	int else_cnt = 0;
	
	if (file.is_open()) {
		string line;
		// Procesamos el archivo
		while (getline(file, line)) {
			int start = 0;
			while (!is_valid_char(line[start]))
				start++;
			
			// Reemplazamos los espacios que no sean una indentación
			// por un caracter vacío.
			//replace(line.begin() + start, line.end(), ' ', '\0');
			inst.push_back(line);
		}
				
		int lines = (int) inst.size();
		
		// Agregamos todas las variables posibles al grafo
		for (int i = 97; i <= 122; i++) {
			// Si la i-ésima línea es false, entonces esa variable
			// no aparece en esa línea.
			vector <bool> v(lines, false);
			// Inicializo todas las variables posibles con un vector 
			// lleno de false.
			graph[char(i)] = v;
		}
			
		// Primer recorrido: para crear la lista de adyacencia
		for (int i = 0; i < lines; i++) {
			char* curr_inst = string_to_array(inst[i]);
			
			bool is_while = strncmp("while", curr_inst, 5) == 0;
			bool is_if = strncmp("if", curr_inst, 2) == 0;
			bool is_else = strncmp("else", curr_inst, 4) == 0;
			
			if (is_while) {
				if (i == 0)
					// Si es la primera línea, no puede haber código
					while_nc_cnt += 1;
				else {
					char* prev_inst = string_to_array(inst[i-1]);
					// Sino, depende si la línea anterior empieza o no
					// con un while (si es true, se considera que no
					// hay código entremedio).
					bool has_code = strncmp("while", prev_inst, 5) != 0;
					if (has_code)
						while_c_cnt += 1;
					else
						while_nc_cnt += 1;
				}
			} 
			
			else if (is_if) {
				if_cnt += 1;
			}
			 
			else if (is_else) {
				else_cnt += 1;
			}
			
			/*	
			// Leemos el largo de la i-ésima instrucción
			int inst_size = (int) inst[i].size();
			for (int j = 0; j < inst_size; j++) {
				char curr = inst[i][j];
				
				if (is_valid_char(curr)) {
					
					if (is_w
					
					string res = "";
					while (is_valid_char(curr)) {
						res += curr;
						char next = inst[i][j+1];
						
						// Caso función (p. ej. f(x, y))
						// Ojo: inst[i][j+2] existe porque suponemos
						// que no hay errores de sintaxis.
						if (next == '(') {
							// Procesar las variables
							while (next != ')') {
								
							}
							
						}
							
								
						else if (next == ',')
							
						
						curr = next;
					}
				}
				graph[curr] = 1;
			}*/
		}
		
		int nodes = if_cnt + else_cnt + while_c_cnt * 3 \
			+ while_nc_cnt * 2 + 1;
			
		cout << nodes << '\n';

		file.close();
	}
	
	return 0;
}
