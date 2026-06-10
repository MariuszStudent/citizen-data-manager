# ============================================================
# CITIZEN DATA MANAGER - Algorytmy zaawansowane i struktury danych
# Mariusz S. - nr 8600
# ============================================================
# Uruchamianie:
#   python citizen_manager.py        -> CLI
#   python citizen_manager.py test   -> testy
#   python citizen_manager.py gui    -> okno Tkinter
#   python citizen_manager.py api    -> FastAPI
# ============================================================

import sys
import os
import json
import sqlite3
import unittest
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional


LOG_FILE = "log.txt"


def log_action(text: str):
    """Prosty zapis operacji do pliku log.txt."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{now} - {text}\n")


# ============================================================
# 1. MODEL DANYCH
# ============================================================

@dataclass
class Citizen:
    id: str
    first_name: str
    last_name: str
    age: int

    def __repr__(self):
        return f"{self.id} | {self.first_name} {self.last_name} | {self.age} lat"


# ============================================================
# 2. LISTA WIĄZANA
# ============================================================

class Node:
    def __init__(self, data: Citizen):
        self.data = data
        self.next: Optional["Node"] = None


class LinkedList:
    def __init__(self):
        self.head: Optional[Node] = None

    def insert_at_beginning(self, data: Citizen):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def delete_by_id(self, citizen_id: str) -> bool:
        temp = self.head
        prev = None

        while temp and temp.data.id != citizen_id:
            prev = temp
            temp = temp.next

        if not temp:
            return False

        if prev:
            prev.next = temp.next
        else:
            self.head = temp.next

        return True

    def to_list(self) -> List[Citizen]:
        arr: List[Citizen] = []
        temp = self.head
        while temp:
            arr.append(temp.data)
            temp = temp.next
        return arr

    def clear(self):
        self.head = None


# ============================================================
# 3. STOS - HISTORIA UNDO
# ============================================================

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.items:
            return self.items.pop()
        return None


# ============================================================
# 4. KOLEJKA - REJESTRACJA
# ============================================================

class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.items:
            return self.items.pop(0)
        return None

    def size(self):
        return len(self.items)


# ============================================================
# 5. REPOZYTORIUM SQLITE
# ============================================================

class CitizenRepository:
    def __init__(self, db_path: str = "citizens.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS citizens (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def add(self, citizen: Citizen):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO citizens (id, first_name, last_name, age) VALUES (?, ?, ?, ?)",
            (citizen.id, citizen.first_name, citizen.last_name, citizen.age)
        )
        self.conn.commit()

    def update(self, citizen: Citizen) -> bool:
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE citizens SET first_name = ?, last_name = ?, age = ? WHERE id = ?",
            (citizen.first_name, citizen.last_name, citizen.age, citizen.id)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def delete(self, citizen_id: str):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM citizens WHERE id = ?", (citizen_id,))
        self.conn.commit()

    def get_all(self) -> List[Citizen]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, first_name, last_name, age FROM citizens")
        rows = cur.fetchall()
        return [Citizen(*row) for row in rows]

    def close(self):
        self.conn.close()


# ============================================================
# 6. WYSZUKIWANIE
# ============================================================

def linear_search(arr: List[Citizen], target_id: str) -> int:
    for i, citizen in enumerate(arr):
        if citizen.id == target_id:
            return i
    return -1


def binary_search(arr: List[Citizen], target_id: str) -> int:
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid].id == target_id:
            return mid
        if arr[mid].id < target_id:
            left = mid + 1
        else:
            right = mid - 1

    return -1


# ============================================================
# 7. SORTOWANIE PO ID
# ============================================================

def bubble_sort(arr: List[Citizen]) -> None:
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if arr[j].id > arr[j + 1].id:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]


def selection_sort(arr: List[Citizen]) -> None:
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j].id < arr[min_idx].id:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]


def insertion_sort(arr: List[Citizen]) -> None:
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j].id > key.id:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key


def merge_sort(arr: List[Citizen]) -> List[Citizen]:
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)


def merge(left: List[Citizen], right: List[Citizen]) -> List[Citizen]:
    result: List[Citizen] = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i].id <= right[j].id:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(arr: List[Citizen]) -> List[Citizen]:
    if len(arr) <= 1:
        return arr

    pivot = arr[-1]
    left = [x for x in arr[:-1] if x.id <= pivot.id]
    right = [x for x in arr[:-1] if x.id > pivot.id]
    return quick_sort(left) + [pivot] + quick_sort(right)


# ============================================================
# 8. SERWIS - LOGIKA PROGRAMU
# ============================================================

class CitizenService:
    def __init__(self, repo: CitizenRepository):
        self.repo = repo
        self.citizens = LinkedList()
        self.history = Stack()
        self.registration_queue = Queue()
        self._load_from_db()

    def _load_from_db(self):
        self.citizens.clear()
        for c in self.repo.get_all():
            self.citizens.insert_at_beginning(c)

    def _set_list(self, arr: List[Citizen]):
        self.citizens.clear()
        for c in reversed(arr):
            self.citizens.insert_at_beginning(c)

    def add_citizen(self, citizen: Citizen):
        self.citizens.insert_at_beginning(citizen)
        self.repo.add(citizen)
        self.history.push(("add", citizen))
        log_action(f"Dodano obywatela {citizen.id}")

    def delete_citizen(self, citizen_id: str) -> bool:
        arr = self.citizens.to_list()
        idx = linear_search(arr, citizen_id)
        if idx == -1:
            log_action(f"Nieudane usuwanie, brak ID {citizen_id}")
            return False

        citizen = arr[idx]
        self.history.push(("delete", citizen))
        deleted = self.citizens.delete_by_id(citizen_id)
        if deleted:
            self.repo.delete(citizen_id)
            log_action(f"Usunieto obywatela {citizen_id}")
        return deleted

    def update_citizen(self, citizen_id: str, new_data: Citizen) -> bool:
        arr = self.citizens.to_list()
        idx = linear_search(arr, citizen_id)
        if idx == -1:
            log_action(f"Nieudana aktualizacja, brak ID {citizen_id}")
            return False

        old_citizen = arr[idx]
        new_data.id = citizen_id
        arr[idx] = new_data
        self._set_list(arr)
        self.repo.update(new_data)
        self.history.push(("update", old_citizen, new_data))
        log_action(f"Zaktualizowano obywatela {citizen_id}")
        return True

    def list_citizens(self) -> List[Citizen]:
        return self.citizens.to_list()

    def sort_citizens(self, algorithm: str) -> None:
        arr = self.citizens.to_list()

        if algorithm == "bubble":
            bubble_sort(arr)
        elif algorithm == "selection":
            selection_sort(arr)
        elif algorithm == "insertion":
            insertion_sort(arr)
        elif algorithm == "merge":
            arr = merge_sort(arr)
        elif algorithm == "quick":
            arr = quick_sort(arr)
        else:
            return

        self._set_list(arr)
        log_action(f"Posortowano lista algorytmem {algorithm}")

    def sort_by_last_name(self):
        arr = self.citizens.to_list()
        arr.sort(key=lambda c: c.last_name.lower())
        self._set_list(arr)
        log_action("Posortowano po nazwisku")

    def search_citizen(self, citizen_id: str, method: str = "linear") -> int:
        arr = self.citizens.to_list()
        if method == "linear":
            return linear_search(arr, citizen_id)

        arr = merge_sort(arr)
        return binary_search(arr, citizen_id)

    def get_citizen_by_id(self, citizen_id: str) -> Optional[Citizen]:
        arr = self.citizens.to_list()
        idx = linear_search(arr, citizen_id)
        if idx == -1:
            return None
        return arr[idx]

    def enqueue_registration(self, citizen_id: str):
        self.registration_queue.enqueue(citizen_id)
        log_action(f"Dodano do kolejki rejestracji {citizen_id}")

    def dequeue_registration(self) -> Optional[str]:
        citizen_id = self.registration_queue.dequeue()
        log_action(f"Obsluzono kolejke, wynik: {citizen_id}")
        return citizen_id

    def export_to_json(self, file_name: str = "citizens.json") -> str:
        data = [asdict(c) for c in self.list_citizens()]
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        log_action(f"Wyeksportowano dane do {file_name}")
        return file_name

    def undo(self):
        op = self.history.pop()
        if not op:
            return False

        action = op[0]

        if action == "add":
            citizen = op[1]
            self.citizens.delete_by_id(citizen.id)
            self.repo.delete(citizen.id)
            log_action(f"Undo: cofnieto dodanie {citizen.id}")

        elif action == "delete":
            citizen = op[1]
            self.citizens.insert_at_beginning(citizen)
            self.repo.add(citizen)
            log_action(f"Undo: cofnieto usuniecie {citizen.id}")

        elif action == "update":
            old_citizen = op[1]
            arr = self.citizens.to_list()
            idx = linear_search(arr, old_citizen.id)
            if idx != -1:
                arr[idx] = old_citizen
                self._set_list(arr)
                self.repo.update(old_citizen)
                log_action(f"Undo: cofnieto aktualizacje {old_citizen.id}")

        return True


# ============================================================
# 9. CLI
# ============================================================

def run_cli():
    repo = CitizenRepository()
    service = CitizenService(repo)

    while True:
        print("\n--- SYSTEM OBYWATELI (CLI) ---")
        print("1. Dodaj obywatela")
        print("2. Usun obywatela")
        print("3. Wyswietl wszystkich")
        print("4. Sortuj")
        print("5. Szukaj")
        print("6. Dodaj do kolejki rejestracji")
        print("7. Obsluz kolejke")
        print("8. Cofnij ostatnia operacje")
        print("9. Eksportuj do JSON")
        print("10. Aktualizuj obywatela")
        print("0. Wyjscie")

        choice = input("Wybierz: ")

        if choice == "1":
            cid = input("ID: ")
            fn = input("Imie: ")
            ln = input("Nazwisko: ")
            try:
                age = int(input("Wiek: "))
            except ValueError:
                print("Wiek musi byc liczba.")
                continue
            service.add_citizen(Citizen(cid, fn, ln, age))
            print("Dodano.")

        elif choice == "2":
            cid = input("Podaj ID do usuniecia: ")
            if service.delete_citizen(cid):
                print("Usunieto.")
            else:
                print("Nie znaleziono.")

        elif choice == "3":
            for c in service.list_citizens():
                print(c)

        elif choice == "4":
            print("1. Bubble 2. Selection 3. Insertion 4. Merge 5. Quick 6. Nazwisko")
            s = input("Wybierz algorytm: ")
            mapping = {
                "1": "bubble",
                "2": "selection",
                "3": "insertion",
                "4": "merge",
                "5": "quick",
            }
            if s == "6":
                service.sort_by_last_name()
                print("Posortowano po nazwisku.")
            elif s in mapping:
                service.sort_citizens(mapping[s])
                print("Posortowano po ID.")
            else:
                print("Nieznany algorytm.")

        elif choice == "5":
            cid = input("Podaj ID: ")
            print("1. Linear 2. Binary")
            s = input("Wybierz: ")
            method = "linear" if s == "1" else "binary"
            idx = service.search_citizen(cid, method)
            print("Znaleziono!" if idx != -1 else "Brak wyniku.")

        elif choice == "6":
            cid = input("ID do rejestracji: ")
            service.enqueue_registration(cid)
            print("Dodano do kolejki.")

        elif choice == "7":
            handled = service.dequeue_registration()
            print("Obsluzono:", handled)

        elif choice == "8":
            if service.undo():
                print("Cofnieto.")
            else:
                print("Brak operacji do cofniecia.")

        elif choice == "9":
            file_name = service.export_to_json()
            print("Zapisano plik:", file_name)

        elif choice == "10":
            cid = input("ID osoby do aktualizacji: ")
            fn = input("Nowe imie: ")
            ln = input("Nowe nazwisko: ")
            try:
                age = int(input("Nowy wiek: "))
            except ValueError:
                print("Wiek musi byc liczba.")
                continue
            if service.update_citizen(cid, Citizen(cid, fn, ln, age)):
                print("Zaktualizowano.")
            else:
                print("Nie znaleziono ID.")

        elif choice == "0":
            repo.close()
            break

        else:
            print("Nie ma takiej opcji.")


# ============================================================
# 10. GUI TKINTER
# ============================================================

def run_gui():
    import tkinter as tk
    from tkinter import messagebox

    repo = CitizenRepository()
    service = CitizenService(repo)

    root = tk.Tk()
    root.title("Citizen Manager")

    listbox = tk.Listbox(root, width=70)
    listbox.pack(padx=10, pady=10)

    def refresh_list(items=None):
        listbox.delete(0, tk.END)
        data = items if items is not None else service.list_citizens()
        for c in data:
            listbox.insert(tk.END, str(c))

    def add_citizen_gui():
        cid = entry_id.get().strip()
        fn = entry_fn.get().strip()
        ln = entry_ln.get().strip()
        try:
            age = int(entry_age.get())
        except ValueError:
            messagebox.showerror("Blad", "Wiek musi byc liczba.")
            return

        if not cid or not fn or not ln:
            messagebox.showerror("Blad", "Uzupelnij ID, imie i nazwisko.")
            return

        service.add_citizen(Citizen(cid, fn, ln, age))
        refresh_list()

    def delete_citizen_gui():
        selection = listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Najpierw zaznacz osobe.")
            return
        line = listbox.get(selection[0])
        cid = line.split("|")[0].strip()
        service.delete_citizen(cid)
        refresh_list()

    def sort_last_name_gui():
        service.sort_by_last_name()
        refresh_list()

    def search_gui():
        cid = entry_search.get().strip()
        citizen = service.get_citizen_by_id(cid)
        if citizen:
            refresh_list([citizen])
        else:
            messagebox.showinfo("Wynik", "Nie znaleziono osoby o takim ID.")

    def close_gui():
        repo.close()
        root.destroy()

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=5)

    tk.Label(frame, text="ID").grid(row=0, column=0)
    tk.Label(frame, text="Imie").grid(row=1, column=0)
    tk.Label(frame, text="Nazwisko").grid(row=2, column=0)
    tk.Label(frame, text="Wiek").grid(row=3, column=0)

    entry_id = tk.Entry(frame)
    entry_fn = tk.Entry(frame)
    entry_ln = tk.Entry(frame)
    entry_age = tk.Entry(frame)

    entry_id.grid(row=0, column=1)
    entry_fn.grid(row=1, column=1)
    entry_ln.grid(row=2, column=1)
    entry_age.grid(row=3, column=1)

    search_frame = tk.Frame(root)
    search_frame.pack(padx=10, pady=5)
    tk.Label(search_frame, text="Szukaj ID").grid(row=0, column=0)
    entry_search = tk.Entry(search_frame)
    entry_search.grid(row=0, column=1)

    btn_add = tk.Button(root, text="Dodaj", command=add_citizen_gui)
    btn_del = tk.Button(root, text="Usun zaznaczonego", command=delete_citizen_gui)
    btn_refresh = tk.Button(root, text="Odswiez", command=refresh_list)
    btn_sort = tk.Button(root, text="Sortuj po nazwisku", command=sort_last_name_gui)
    btn_search = tk.Button(root, text="Szukaj po ID", command=search_gui)

    btn_add.pack(pady=2)
    btn_del.pack(pady=2)
    btn_sort.pack(pady=2)
    btn_search.pack(pady=2)
    btn_refresh.pack(pady=2)

    refresh_list()
    root.protocol("WM_DELETE_WINDOW", close_gui)
    root.mainloop()


# ============================================================
# 11. API FASTAPI
# ============================================================

def run_api():
    from fastapi import FastAPI, HTTPException
    import uvicorn

    repo = CitizenRepository()
    service = CitizenService(repo)
    app = FastAPI(title="Citizen Manager API")

    @app.get("/citizens")
    def get_citizens():
        return service.list_citizens()

    @app.post("/citizens")
    def add_citizen(citizen: Citizen):
        service.add_citizen(citizen)
        return {"status": "ok"}

    @app.put("/citizens/{citizen_id}")
    def update_citizen(citizen_id: str, citizen: Citizen):
        if not service.update_citizen(citizen_id, citizen):
            raise HTTPException(status_code=404, detail="Citizen not found")
        return {"status": "updated"}

    @app.delete("/citizens/{citizen_id}")
    def delete_citizen(citizen_id: str):
        if not service.delete_citizen(citizen_id):
            raise HTTPException(status_code=404, detail="Citizen not found")
        return {"status": "deleted"}

    @app.get("/citizens/search/{citizen_id}")
    def search_citizen_api(citizen_id: str):
        citizen = service.get_citizen_by_id(citizen_id)
        if not citizen:
            raise HTTPException(status_code=404, detail="Citizen not found")
        return citizen

    @app.get("/citizens/sort/{algorithm}")
    def sort_citizens_api(algorithm: str):
        if algorithm == "last_name":
            service.sort_by_last_name()
        else:
            service.sort_citizens(algorithm)
        return service.list_citizens()

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
    repo.close()


# ============================================================
# 12. TESTY JEDNOSTKOWE
# ============================================================

class TestCitizenManager(unittest.TestCase):

    def setUp(self):
        self.repo = CitizenRepository(":memory:")
        self.service = CitizenService(self.repo)

    def tearDown(self):
        self.repo.close()

    def test_add_and_list(self):
        self.service.add_citizen(Citizen("1", "Jan", "Kowalski", 30))
        self.assertEqual(len(self.service.list_citizens()), 1)

    def test_delete(self):
        self.service.add_citizen(Citizen("1", "Jan", "Kowalski", 30))
        self.assertTrue(self.service.delete_citizen("1"))
        self.assertEqual(len(self.service.list_citizens()), 0)

    def test_sort(self):
        self.service.add_citizen(Citizen("3", "Adam", "Nowak", 20))
        self.service.add_citizen(Citizen("1", "Jan", "Kowalski", 30))
        self.service.add_citizen(Citizen("2", "Ola", "Wisla", 25))
        self.service.sort_citizens("merge")
        ids = [c.id for c in self.service.list_citizens()]
        self.assertEqual(ids, ["1", "2", "3"])

    def test_search(self):
        self.service.add_citizen(Citizen("1", "Jan", "Kowalski", 30))
        self.assertNotEqual(self.service.search_citizen("1", "linear"), -1)
        self.assertNotEqual(self.service.search_citizen("1", "binary"), -1)
        self.assertEqual(self.service.search_citizen("100", "linear"), -1)

    def test_undo(self):
        self.service.add_citizen(Citizen("1", "Jan", "Kowalski", 30))
        self.assertTrue(self.service.undo())
        self.assertEqual(len(self.service.list_citizens()), 0)

    def test_queue_registration(self):
        self.service.enqueue_registration("1")
        self.service.enqueue_registration("2")
        self.assertEqual(self.service.registration_queue.size(), 2)
        self.assertEqual(self.service.dequeue_registration(), "1")
        self.assertEqual(self.service.dequeue_registration(), "2")
        self.assertIsNone(self.service.dequeue_registration())

    def test_update_citizen(self):
        self.service.add_citizen(Citizen("1", "Jan", "Kowalski", 30))
        ok = self.service.update_citizen("1", Citizen("1", "Adam", "Nowak", 40))
        self.assertTrue(ok)
        citizen = self.service.get_citizen_by_id("1")
        self.assertEqual(citizen.first_name, "Adam")
        self.assertEqual(citizen.last_name, "Nowak")
        self.assertEqual(citizen.age, 40)

    def test_sort_by_last_name(self):
        self.service.add_citizen(Citizen("1", "Jan", "Zielinski", 30))
        self.service.add_citizen(Citizen("2", "Adam", "Kowalski", 20))
        self.service.sort_by_last_name()
        names = [c.last_name for c in self.service.list_citizens()]
        self.assertEqual(names, ["Kowalski", "Zielinski"])

    def test_export_json(self):
        file_name = "test_citizens.json"
        if os.path.exists(file_name):
            os.remove(file_name)
        self.service.add_citizen(Citizen("1", "Jan", "Kowalski", 30))
        self.service.export_to_json(file_name)
        self.assertTrue(os.path.exists(file_name))
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data[0]["id"], "1")
        os.remove(file_name)


GITHUB_WORKFLOW_YAML = """
name: Python CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python citizen_manager.py test
"""


# ============================================================
# 13. START PROGRAMU
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = os.environ.get("MODE", "cli")

    if mode == "test":
        unittest.main(argv=[sys.argv[0]])
    elif mode == "gui":
        run_gui()
    elif mode == "api":
        run_api()
    else:
        run_cli()
