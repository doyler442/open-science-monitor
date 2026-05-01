// venues-data.js — Auto-updated by Open Science Policy Monitor
// Last updated: 2026-05-01
// Manual edits will be overwritten on next monitor run.

const COLS = ['Open Access','Preprint','Open Data','Open Materials','Open Artefact','Registered Reports','Open Peer Review','Replication'];

// 0 = absent, 1 = partial (~), 2 = present (✓)
const rows = [
  // SECTION: SENIOR SCHOLARS' LIST OF PREMIER JOURNALS
  { section: "Senior Scholars' List of Premier Journals" },
  { name: 'Decision Support Systems', abbr: 'DSS', url: 'https://www.sciencedirect.com/journal/decision-support-systems', vals: [1,2,2,2,0,0,0,0] },
  { name: 'European Journal of Information Systems', abbr: 'EJIS', url: 'https://www.tandfonline.com/journals/tjis20', vals: [1,1,0,0,0,0,0,0] },
  { name: 'Information &amp; Management', abbr: 'I&M', url: 'https://www.sciencedirect.com/journal/information-and-management', vals: [1,2,0,0,0,0,0,0] },
  { name: 'Information and Organization', abbr: 'I&O', url: 'https://www.sciencedirect.com/journal/information-and-organization', vals: [1,2,0,0,0,0,0,0] },
  { name: 'Information Systems Journal', abbr: 'ISJ', url: 'https://onlinelibrary.wiley.com/journal/13652575', vals: [1,2,2,1,0,0,0,0] },
  { name: 'Information Systems Research', abbr: 'ISR', url: 'https://pubsonline.informs.org/journal/isre', vals: [1,0,0,0,0,0,0,0] },
  { name: 'Journal of the Association for Information Systems', abbr: 'JAIS', url: 'https://aisel.aisnet.org/jais/', vals: [1,0,1,0,0,0,0,0] },
  { name: 'Journal of Information Technology', abbr: 'JIT', url: 'https://journals.sagepub.com/home/jin', vals: [1,0,0,0,0,0,0,0] },
  { name: 'Journal of Management Information Systems', abbr: 'JMIS', url: 'https://www.tandfonline.com/journals/mmis20', vals: [1,1,0,0,0,0,0,0] },
  { name: 'Journal of Strategic Information Systems', abbr: 'JSIS', url: 'https://www.sciencedirect.com/journal/the-journal-of-strategic-information-systems', vals: [1,2,0,0,0,0,0,0] },
  { name: 'MIS Quarterly', abbr: 'MISQ', url: 'https://misq.umn.edu/', vals: [1,0,1,1,0,0,0,0] },
  // SECTION: AIS JOURNALS
  { section: "AIS Journals" },
  { name: 'Communications of the Association for Information Systems', abbr: 'CAIS', url: 'https://aisel.aisnet.org/cais/', vals: [2,0,0,0,0,0,2,2] },
  { name: 'Business &amp; Information Systems Engineering', abbr: 'BISE', url: 'https://www.bise-journal.com/', vals: [1,0,0,0,0,1,0,0] },
  { name: 'Australasian Journal of Information Systems', abbr: 'AJIS', url: 'https://ajis.aaisnet.org/', vals: [2,0,1,0,0,0,0,0] },
  // SECTION: MAJOR CONFERENCES
  { section: "Major Conferences" },
  { name: 'International Conference on Information Systems', abbr: 'ICIS', url: 'https://aisel.aisnet.org/icis/', vals: [0,0,0,0,0,0,0,0] },
  { name: 'European Conference on Information Systems', abbr: 'ECIS', url: 'https://aisel.aisnet.org/ecis/', vals: [0,0,0,0,0,0,0,0] },
  { name: 'Americas Conference on Information Systems', abbr: 'AMCIS', url: 'https://aisel.aisnet.org/amcis/', vals: [0,1,0,0,0,0,0,0] },
  { name: 'Hawaii International Conference on System Sciences', abbr: 'HICSS', url: 'https://hicss.hawaii.edu/', vals: [2,0,0,0,0,0,0,0] },
  { name: 'Design Science Research in Information Systems and Technology', abbr: 'DESRIST', url: 'https://desrist.org/', vals: [0,0,0,0,0,0,0,0] },
];
