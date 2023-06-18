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

char* recognizeInst(int id_line, string inst) {
	string tabs(id_line, '\t');
	tabs += inst;

	return string_to_array(tabs);
}

int main() {
	fstream file;
	// ios::in para leer el archivo
	file.open("prueba.txt", ios::in);
	
	vector <vector <int>> adj;
	vector <string> lines;
	vector <int> blocks;
	
	if (file.is_open()) {
		string line;
		// Procesamos el archivo y los bloques
		int i = 0, indexBlocks = 1, last_id = -1;
		while (getline(file, line)) {
			lines.push_back(line);
			char* line_ = string_to_array(line);

			int id_line = identation(line, "", 1);

			char* token_if = recognizeInst(id_line, "if");
			char* token_else = recognizeInst(id_line, "else");
			char* token_while = recognizeInst(id_line, "while");
			
			// Revisa si la línea actual empieza con "if"...
			if (!strncmp(token_if, line_, 2 + id_line)) {
				blocks.push_back(indexBlocks);
				indexBlocks++;
			}

			// ...o con "else"...
			else if (!strncmp(token_else, line_, 4 + id_line)) {					
				blocks.push_back(indexBlocks);
				indexBlocks++;
			}
			
			// ...o con "while"
			else if (!strncmp(token_while, line_, 5 + id_line)) {
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
		
		for (int j=0; j < (int) blocks.size(); j++) {
			//cout << "j: " << j << '\n';
			cout << lines[j] << ' ' << blocks[j] << '\n';
		}
		
		file.close();
	}
	
	int nodo_sz = (int) blocks.size();
	for (int i=1; i<nodo_sz; i++) {
		// Están en bloques distintos
		if (blocks[i] != blocks[i-1]) {
			
			// while
			// if
			// else
		}
	}
	
	return 0;
}
