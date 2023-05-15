#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
#define print(x) cout << x << '\n';

// Un número lo suficientemente chico
ll best_ans = -1e18;

// Función recursiva 
// solve(v, i) := respuesta al problema hasta el índice "i"
ll solve(vector<ll> &v, vector<ll> &indices, int i) {
	// Si i >= v.size(), el problema no tiene solución
	// entonces retornamos la más cercana
	int n = (int) v.size();
	if (i >= n)
		return solve(v, indices, n-1);
		
	indices.assign(n, 0);
	
	// Casos base
	if (i == 0) {
		indices[0] = 1;
		return v[0];
	} else if (i == 1) {
		ll MX = max(v[0], v[1]);
		if (MX == v[0]) {
			indices[0] = 1;
			indices[1] = 0;
		} else {
			indices[1] = 1;
			indices[0] = 0;
		}
		
		return MX;
	} else {
		// Caso recursivo (O(2^n))
		// Valoración actual
		ll act = v[i];
		// Valoración considerando no-adyacencia
		ll ady = v[i] + solve(v, indices, i-2);
		ll resp = max(act, ady);

		if (resp < best_ans)
			return best_ans;
		
		if (resp == act) {
			indices.assign(n, 0);
			indices[i] = 1;
		} else {
			indices[i] = 1;
			indices[i-1] = 0;
		}
		
		best_ans = max(best_ans, resp);
		return resp;
	}
}

int main() {
	int n; cin >> n;
	vector <ll> v(n);
	
	vector <vector<ll>> indices;
	vector <ll> resp(n, 0);
	indices.assign(n, resp);

	for (int i=0; i<n; i++)
		cin >> v[i];

	// ans:=respuesta, type:=0, 1 o 2
	ll ans, type = -1;
	
	if (n >= 3) {
		ll ans_I = solve(v, indices[1], n-1);
		ll ans_P = solve(v, indices[2], n-2);
		
		ans = max(ans_I, ans_P);
		
		if (ans == ans_I)
			type = 1;
		else
			type = 2;
	} else {
		ans = solve(v, indices[0], n-1);
		type = 0;
	}
	
	for (int i=0; i<n; i++)
		if (indices[type][i] == 1)
			cout << (i + 1) << ' ';
		
	cout << '\n' << ans;
	return 0;
}
