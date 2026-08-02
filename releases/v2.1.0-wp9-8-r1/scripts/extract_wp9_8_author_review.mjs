import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const root = path.resolve(import.meta.dirname, "..", "..");
const inputPath = path.join(
  root,
  "outputs",
  "wp9_8_author_review_2026-08-01",
  "WP9_8_AUTHOR_REVIEW_WORKBOOK.xlsx",
);
const fieldOutput = path.join(root, "evidence", "WP9_8_R1_AUTHOR_VERIFIED_FIELD_OVERRIDES.csv");
const methodOutput = path.join(root, "evidence", "WP9_8_R1_AUTHOR_VERIFIED_METHOD_MAPPINGS.csv");
const lockOutput = path.join(root, "validation", "WP9_8_R1_SOURCE_LOCK.json");

const expectedHash = "3ece3b766ddcd28748301a1f3b894a6012dcf9d2a3a1aea810f645303c29e1fe";
const expectedReviewer = "Yangqi Ma";
const expectedDate = "2026-08-01";
const expectedInitials = "YM";

function clean(value) {
  if (value === null || value === undefined) return "";
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  return String(value).trim();
}

function csvEscape(value) {
  const text = clean(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function csvText(rows, fields) {
  return `${fields.map(csvEscape).join(",")}\r\n${rows
    .map((row) => fields.map((field) => csvEscape(row[field])).join(","))
    .join("\r\n")}\r\n`;
}

function normalizeDate(value) {
  const text = clean(value);
  if (/^\d{4}-\d{2}-\d{2}/.test(text)) return text.slice(0, 10);
  const serial = Number(text);
  if (Number.isFinite(serial) && serial > 1000) {
    const utc = Date.UTC(1899, 11, 30) + serial * 86400000;
    return new Date(utc).toISOString().slice(0, 10);
  }
  return text;
}

function readTable(workbook, sheetName, address) {
  const sheet = workbook.worksheets.getItem(sheetName);
  const values = sheet.getRange(address).values;
  const headers = values[0].map(clean);
  const rows = values.slice(1).filter((row) => clean(row[0]) !== "");
  return rows.map((row) => Object.fromEntries(headers.map((header, index) => [header, row[index]])));
}

function requireValue(row, field, itemId) {
  const value = clean(row[field]);
  if (!value) throw new Error(`${itemId}: missing ${field}`);
  return value;
}

function verifySignature(row) {
  const itemId = clean(row.review_item_id);
  if (clean(row.row_completion).toLowerCase() !== "complete") {
    throw new Error(`${itemId}: row_completion is not complete`);
  }
  if (clean(row.reviewer_name) !== expectedReviewer) {
    throw new Error(`${itemId}: unexpected reviewer ${clean(row.reviewer_name)}`);
  }
  if (normalizeDate(row.review_date) !== expectedDate) {
    throw new Error(`${itemId}: unexpected review date ${normalizeDate(row.review_date)}`);
  }
  if (clean(row.signature_or_initials) !== expectedInitials) {
    throw new Error(`${itemId}: unexpected signature ${clean(row.signature_or_initials)}`);
  }
}

const bytes = await fs.readFile(inputPath);
const actualHash = crypto.createHash("sha256").update(bytes).digest("hex");
if (actualHash !== expectedHash) {
  throw new Error(`Workbook SHA256 changed: ${actualHash}`);
}

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const fieldRows = readTable(workbook, "51_Field_Rechecks", "A9:AG60");
const methodRows = readTable(workbook, "9_Method_Mappings", "A9:AB18");

if (fieldRows.length !== 51) throw new Error(`Expected 51 field rows, found ${fieldRows.length}`);
if (methodRows.length !== 9) throw new Error(`Expected 9 method rows, found ${methodRows.length}`);

const fieldOutputRows = fieldRows.map((row) => {
  verifySignature(row);
  const itemId = requireValue(row, "review_item_id", "field row");
  const finalScore = requireValue(row, "final_score", itemId);
  if (!/^[0-4]$/.test(finalScore)) throw new Error(`${itemId}: invalid final_score ${finalScore}`);
  return {
    review_item_id: itemId,
    paper_id: requireValue(row, "paper_id", itemId),
    dimension: requireValue(row, "dimension", itemId),
    category_field: requireValue(row, "current_category_field", itemId),
    prior_category: clean(row.current_category),
    final_category: requireValue(row, "final_category", itemId),
    score_field: requireValue(row, "current_score_field", itemId),
    prior_score: clean(row.current_score),
    final_score: finalScore,
    score_state: requireValue(row, "score_state", itemId),
    evidence_page_or_section: requireValue(row, "evidence_page_or_section", itemId),
    decision_rationale: requireValue(row, "decision_rationale", itemId),
    review_decision: requireValue(row, "review_decision", itemId),
    reviewer_name: clean(row.reviewer_name),
    reviewer_affiliation: clean(row.reviewer_affiliation),
    review_date: normalizeDate(row.review_date),
    signature_or_initials: clean(row.signature_or_initials),
    row_completion: clean(row.row_completion),
    source_workbook_sha256: actualHash,
  };
});

const methodOutputRows = methodRows.map((row) => {
  verifySignature(row);
  const itemId = requireValue(row, "review_item_id", "method row");
  return {
    review_item_id: itemId,
    paper_id: requireValue(row, "paper_id", itemId),
    prior_primary_family: clean(row.current_primary_family),
    final_primary_family: requireValue(row, "final_primary_family", itemId),
    prior_secondary_family: clean(row.current_secondary_family),
    final_secondary_family: clean(row.final_secondary_family),
    evidence_page_or_section: requireValue(row, "evidence_page_or_section", itemId),
    decision_rationale: requireValue(row, "decision_rationale", itemId),
    review_decision: requireValue(row, "review_decision", itemId),
    reviewer_name: clean(row.reviewer_name),
    reviewer_affiliation: clean(row.reviewer_affiliation),
    review_date: normalizeDate(row.review_date),
    signature_or_initials: clean(row.signature_or_initials),
    row_completion: clean(row.row_completion),
    source_workbook_sha256: actualHash,
  };
});

await fs.mkdir(path.dirname(fieldOutput), { recursive: true });
await fs.mkdir(path.dirname(lockOutput), { recursive: true });
await fs.writeFile(fieldOutput, csvText(fieldOutputRows, Object.keys(fieldOutputRows[0])), "utf8");
await fs.writeFile(methodOutput, csvText(methodOutputRows, Object.keys(methodOutputRows[0])), "utf8");
await fs.writeFile(
  lockOutput,
  JSON.stringify(
    {
      analysis_version: "WP9.8-R1",
      source_workbook: path.relative(root, inputPath).replaceAll("\\", "/"),
      source_workbook_sha256: actualHash,
      extraction_tool: "@oai/artifact-tool",
      field_override_rows: fieldOutputRows.length,
      method_mapping_rows: methodOutputRows.length,
      reviewer: expectedReviewer,
      review_date: expectedDate,
      signature_or_initials: expectedInitials,
      field_output: path.relative(root, fieldOutput).replaceAll("\\", "/"),
      method_output: path.relative(root, methodOutput).replaceAll("\\", "/"),
    },
    null,
    2,
  ) + "\n",
  "utf8",
);

console.log(JSON.stringify({ actualHash, fieldRows: fieldOutputRows.length, methodRows: methodOutputRows.length }, null, 2));
