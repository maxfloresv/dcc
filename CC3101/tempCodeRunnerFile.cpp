da del while
			while (++s < line_size && identations[i] < identations[s]) {
				continue;
			}

			while (++j < s) {
				// Contar cuantas aristas se pasan del scope
				int a = 0;
				for (int k : adj[blocks[j]])
					if (s <= k)
						a++;
				// Borrar aristas correspondientes (sets son ordenados)
				for (int k = 0; k < a; k++) {
					auto last = adj[blocks[j]].end();
					adj[blocks[j]].erase(--last);
				}