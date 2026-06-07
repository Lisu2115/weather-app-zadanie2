# Sprawozdanie: Zadanie 2 – GitHub Actions Pipeline

**Autor:** Mikołaj Lis

## 1. Architektura i cel działania

Celem zadania było utworzenie łańcucha CI/CD w usłudze GitHub Actions. Pipeline automatycznie buduje zoptymalizowany, wieloetapowy obraz Dockerfile dla aplikacji pogodowej (Flask i Requests), a następnie weryfikuje jego bezpieczeństwo. 

* **Publiczne repozytorium obrazów (Push):** GitHub Container Registry (`ghcr.io/lisu2115/weather-app-docker`)
* **Repozytorium Cache:** DockerHub (`lisu2115/weather-app-cache`)

## 2. Realizacja wymagań

### A. Architektura Multi-platform
Zastosowano akcje `docker/setup-qemu-action` oraz `docker/setup-buildx-action`. Pozwalają one na emulację i zbudowanie obrazu wspierającego jednocześnie dwie architektury: **`linux/amd64`** oraz **`linux/arm64`**. Manifest obrazu obsługuje obie platformy docelowe.

### B. Konfiguracja pamięci podręcznej (Cache)
Dane cache budowania są przechowywane w zewnętrznym, publicznym rejestrze na DockerHub. Zastosowano następujące parametry w kroku budowania:
* **Eksporter:** `type=registry`
* **Backend:** `ref=lisu2115/weather-app-cache:latest`
* **Tryb:** `mode=max` (eksportuje cache wszystkich warstw pośrednich dla maksymalnej optymalizacji przyszłych budów).

### C. Test CVE (Trivy) – Gwarancja bezpieczeństwa przed publikacją
Zgodnie z wymaganiami, obraz trafia do `ghcr.io` **tylko wtedy**, gdy nie ma w nim krytycznych i wysokich luk. 
Zastosowano obejście technicznego problemu budowy obrazów multi-platform (lokalny deamon Dockera nie potrafi załadować obrazu multi-platform `tar`). 
**Logika procesu:**
1. Zbudowanie obrazu lokalnie (tylko dla `linux/amd64`) jako tymczasowy obiekt testowy do załadowania do deamona (parametr `load: true`).
2. Uruchomienie skanera **Trivy** na lokalnym obrazie. Skonfigurowano `exit-code: '1'` i `severity: 'CRITICAL,HIGH'`, co sprawia, że w przypadku wykrycia podatności pipeline natychmiast przerywa działanie z błędem (Fail).
3. **Dopiero po zielonym świetle od Trivy** uruchamiane jest finalne budowanie wieloplatformowe (`linux/amd64, linux/arm64`) i wykonanie operacji `push` na `ghcr.io`. 
*Dzięki zapisowi cache na etapie 1, ponowne budowanie w etapie 3 trwa zaledwie ułamki sekund.*

## 3. Strategia tagowania (Tagging Strategy)

Wykorzystano oficjalną akcję `docker/metadata-action` do generowania dynamicznych tagów:
1. **`latest`** – zawsze wskazuje na najnowszy poprawnie zbudowany obraz z gałęzi `main`. Jest to standard ułatwiający pobranie najświeższej, działającej wersji użytkownikowi końcowemu bez znajomości wersji deweloperskiej.
2. **`sha-<short-sha>`** (np. `sha-f2a9c1b`) – tag wygenerowany na podstawie konkretnego commitu Git.
   
**Uzasadnienie:**
Tagowanie hashem commitu to najlepsza praktyka (Best Practice) w obszarze CI/CD i GitOps. Zapewnia **pełną niezmienność i identyfikowalność**. Jeśli na produkcji wystąpi błąd z obrazem, unikalny tag `sha` pozwala w 10 sekund zlokalizować konkretną linijkę kodu i autora zmiany w repozytorium, która ten błąd wprowadziła. Opieranie się wyłącznie na tagu `latest` grozi nadpisaniem historii i brakiem powtarzalności środowiska.

## 4. Dodatkowe informacje
Do autoryzacji z rejestrem DockerHub jako backend cache wykorzystano standardowe sekrety GitHub (`DOCKERHUB_USERNAME` oraz `DOCKERHUB_TOKEN`). Zastosowano również konwersję nazwy repozytorium na małe litery, gdyż GHCR restrykcyjnie odrzuca obrazy zawierające wielkie litery w tagu przestrzeni nazw.

## 5. Potwierdzenie działania
Poniżej znajduje się zrzut ekranu potwierdzające poprawne i pomyślne wykonanie zautomatyzowanego łańcucha (zielony status Action)

![Sukces wykonania GitHub Actions](2.png)

