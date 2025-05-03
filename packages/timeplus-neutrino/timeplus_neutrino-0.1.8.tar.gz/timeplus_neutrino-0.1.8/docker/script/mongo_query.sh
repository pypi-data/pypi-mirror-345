
use lumi_data

db.unstructured_data.drop();

db.createCollection("unstructured_data", {
  changeStreamPreAndPostImages: { enabled: true }
});