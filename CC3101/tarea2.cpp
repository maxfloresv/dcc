#include <bits/stdc++.h>
using namespace std;
using state = vector <int>;

void reflexiva(vector<state> &M, int n) {
	// La diagonal de la matriz debe ser 1 porque todo
	// elemento se relaciona consigo mismo (reflexión)
	for (int i=0; i<n; i++)
		M[i][i] = 1;
}

void simetrica(vector<state> &M, int n) {
	// Si son distintos, uno se relaciona pero no al revés.
	// Por simetría, ambos deben relacionarse (ser 1)
	for (int i=0; i<n; i++)
		for (int j=0; j<n; j++)
			if (M[i][j] != M[j][i])
				M[i][j] = M[j][i] = 1;			
}

void transitiva(vector<state> &M, int n) {
	// aRb y bRc => aRc (transitividad)
	// Cantidad de modificaciones de la transitividad
	int mods = 0;
	while (true) {
		for (int i=0; i<n; i++)
			for (int j=0; j<n; j++)
				for (int k=0; k<n; k++)
					if (M[i][j] == 1 && M[j][k] == 1) {
						// Agregamos una modificación
						if (M[i][k] == 0)
							mods++;
						M[i][k] = 1;
					}
						
		// Si son 0, quiere decir que ya no podemos agregar
		// más elementos con la transitividad
		if (mods == 0)
			break;
		// Vuelve a entrar al ciclo, las modificaciones
		// se deben reiniciar a 0
		mods = 0;
	}
}

int main() {
	int n;
	cin >> n;
	
	// Inicialmente la matriz está con puros 0
	vector <state> M(n, state(n, 0));
	
	for (int i=0; i<n; i++)
		for (int j=0; j<n; j++)
			cin >> M[i][j];
			
	reflexiva(M, n);
	simetrica(M, n);
	transitiva(M, n);
	
	for (int i=0; i<n; i++) {
		for (int j=0; j<n; j++)
			cout << M[i][j] << ' ';
		cout << '\n';
	}
	
	return 0;
}
