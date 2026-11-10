# Baugruppen E07

Modellstruktur und Montagegrenzen; keine vollständige Beschaffungs-/Fertigungsfreigabe. Quelle: data/assembly_structure.json.

| Teilenummer | Baugruppe | direkte Teile / rekursiv | Funktion |
|---|---|---:|---|
| OL-100 | BG10_Gehaeuse | 0 / 59 | bonded structural cabinet; stays assembled during maintenance |
| OL-110 | BG10_Gehaeuse / BG11_Holzstruktur | 13 / 13 | panels, laminated baffle, brace, partition, floor and bonded rear cleats |
| OL-120 | BG10_Gehaeuse / BG12_Feste_Rueckwandgewinde | 30 / 30 | captive steel thread plates and their wood retainer screws remain on cabinet |
| OL-130 | BG10_Gehaeuse / BG13_Elektronikstuetzen | 12 / 12 | fixed tray spacers and floor-side screws/washers remain on cabinet |
| OL-140 | BG10_Gehaeuse / BG14_Kabeldurchfuehrungen | 4 / 4 | fixed speaker feedthroughs and locknuts |
| OL-200 | BG20_Frontbestueckung | 0 / 53 | serviceable acoustic components; baffle stays in cabinet |
| OL-210 | BG20_Frontbestueckung / BG21_Tieftoener | 34 / 34 | LF driver, backing ring, screws, both washers and nuts |
| OL-220 | BG20_Frontbestueckung / BG22_Hochton | 18 / 18 | horn, compression driver and horn fixing hardware; horn-to-driver mounting still open |
| OL-230 | BG20_Frontbestueckung / BG23_Bassreflexport | 1 / 1 | port tube; attachment/sealing still open |
| OL-300 | BG30_Service_Rueckwand | 21 / 21 | removable rear panel and the ten externally removed screws/washers |
| OL-400 | BG40_Elektronikmodul | 0 / 30 | removable electronics module, cables disconnected and tray-top screws removed for extraction |
| OL-410 | BG40_Elektronikmodul / BG41_Traeger | 9 / 9 | removable tray and its top-side service screws/washers |
| OL-420 | BG40_Elektronikmodul / BG42_Verstaerker_DSP | 21 / 21 | JAB PCB outline and its spacers, screws, washers; keepout is separate reference |
| OL-500 | BG50_Kabelbaum | 3 / 3 | DC, LF and HF internal cable jackets; terminals/clips/loops unfinished |
| REF-900 | BG90_Referenzraeume | 2 / 2 | nonphysical hidden clearance reserves; exclude from purchasing BOM |

## Mengen nach Unterbaugruppe

Die Modellmenge beschreibt vorhandene Komponenteninstanzen. Insbesondere Kabel sind hier Konfektionen, keine Meterware; Zuschnitt separat in results/wiring/harness.csv. Nicht modellierte Dichtungen, Kontakte, Clips, Akku und äußere Beschläge fehlen weiterhin. Referenzräume werden nicht eingekauft.

| Unterbaugruppe | Artikel / Referenz | Modellmenge | Einkaufstatus |
|---|---|---:|---|
| BG10_Gehaeuse/BG11_Holzstruktur | Baffle | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Baffle_inner_lamination | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Bottom | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Brace_lower | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Rear_cleat_bottom | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Rear_cleat_left | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Rear_cleat_right | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Rear_cleat_top | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Service_floor | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Service_partition | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Side_left | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Side_right | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG11_Holzstruktur | Top | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG12_Feste_Rueckwandgewinde | Rear_thread_plate_bottom_0.27 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG12_Feste_Rueckwandgewinde | Rear_thread_plate_bottom_0.73 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG12_Feste_Rueckwandgewinde | Rear_thread_plate_left_0.15 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG12_Feste_Rueckwandgewinde | Rear_thread_plate_left_0.5 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG12_Feste_Rueckwandgewinde | Rear_thread_plate_left_0.85 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG12_Feste_Rueckwandgewinde | Rear_thread_plate_right_0.15 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG12_Feste_Rueckwandgewinde | Rear_thread_plate_right_0.5 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG12_Feste_Rueckwandgewinde | Rear_thread_plate_right_0.85 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG12_Feste_Rueckwandgewinde | Rear_thread_plate_top_0.27 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG12_Feste_Rueckwandgewinde | Rear_thread_plate_top_0.73 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG12_Feste_Rueckwandgewinde | wood_pan_2p5x12 | 20 | candidate_exact_head_and_retention_test_pending |
| BG10_Gehaeuse/BG13_Elektronikstuetzen | ISO4762_M3x16 | 4 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG13_Elektronikstuetzen | ISO7089_M3 | 4 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG13_Elektronikstuetzen | WURTH_970100321 | 4 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG10_Gehaeuse/BG14_Kabeldurchfuehrungen | LAPP_53017210 | 2 | DIMENSION_REFERENCE_ONLY_PROCUREMENT_NOT_RELEASED |
| BG10_Gehaeuse/BG14_Kabeldurchfuehrungen | M16x1p5_locknut | 2 | REFERENCE_ONLY; 5mm plastic nut does NOT meet reserved stack |
| BG20_Frontbestueckung/BG21_Tieftoener | ISO4032_M5 | 8 | standard_part_SKU_pending |
| BG20_Frontbestueckung/BG21_Tieftoener | ISO4762_M5x45 | 8 | selected_nominal_fit_physical_check_pending |
| BG20_Frontbestueckung/BG21_Tieftoener | ISO7089_M5 | 16 | standard_part_SKU_pending |
| BG20_Frontbestueckung/BG21_Tieftoener | LF_steel_backing_ring_candidate | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG20_Frontbestueckung/BG21_Tieftoener | REF_Faital_10FE200_4ohm_DATASHEET_ENVELOPE | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG20_Frontbestueckung/BG22_Hochton | DIN934_M4 | 4 | standard_part_SKU_pending |
| BG20_Frontbestueckung/BG22_Hochton | ISO4762_M4x40 | 4 | selected_nominal_fit_physical_check_pending |
| BG20_Frontbestueckung/BG22_Hochton | ISO7089_M4 | 8 | standard_part_SKU_pending |
| BG20_Frontbestueckung/BG22_Hochton | REF_BC_DE10_DATASHEET_ENVELOPE | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG20_Frontbestueckung/BG22_Hochton | REF_BC_ME10V3_DATASHEET_ENVELOPE | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG20_Frontbestueckung/BG23_Bassreflexport | Port_round_candidate | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG30_Service_Rueckwand | ISO4762_M5x40 | 10 | selected_nominal_fit_physical_check_pending |
| BG30_Service_Rueckwand | ISO7089_M5 | 10 | standard_part_SKU_pending |
| BG30_Service_Rueckwand | Rear_removable | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG40_Elektronikmodul/BG41_Traeger | ISO4762_M3x6 | 4 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG40_Elektronikmodul/BG41_Traeger | ISO7089_M3 | 4 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG40_Elektronikmodul/BG41_Traeger | OWN_AL_TRAY_112_90_2 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG40_Elektronikmodul/BG42_Verstaerker_DSP | ISO4762_M3x6 | 8 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG40_Elektronikmodul/BG42_Verstaerker_DSP | ISO7089_M3 | 8 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG40_Elektronikmodul/BG42_Verstaerker_DSP | WONDOM_AA_JA32173 | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG40_Elektronikmodul/BG42_Verstaerker_DSP | WURTH_970100321 | 4 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG50_Kabelbaum | Cordial_CLS215_hf | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG50_Kabelbaum | Cordial_CLS215_lf | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |
| BG50_Kabelbaum | Cordial_CLS215_power | 1 | NOT_QUALIFIED_IN_CURRENT_PROCUREMENT_DATA |

Die enthaltenen historischen Preisbeobachtungen sind nur verknüpfte Quelldaten. Unbekannte Preise, Packmengen und Bezugsquellen wurden nicht ergänzt oder als Nullkosten gerechnet.

Nicht modelliert: BG60_Akkuversorgung, BG70_Schutz_Tragen.
