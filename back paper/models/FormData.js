const mongoose = require('mongoose');

const BackPaperSchema = new mongoose.Schema({
  semester: String,
  courseCode: String,
  courseName: String,
});

const RepeatCourseSchema = new mongoose.Schema({
  semester: String,
  courseCode: String,
  courseName: String,
});

const FormDataSchema = new mongoose.Schema({
  department: { type: String, required: true },
  name: { type: String, required: true },
  fatherName: { type: String, required: true },
  enrollNo: { type: String, required: true },
  programName: { type: String, required: true },
  semesterBatch: { type: String, required: true },
  email: { type: String, required: true },
  feeReceiptNo: { type: Number, required: true },
  amount: { type: Number, required: true },
  feeReceiptFile: { type: String, required: true }, // Path or URL
  backPaper: [BackPaperSchema],
  repeatCourse: [RepeatCourseSchema],
  date: { type: Date, required: true },
  studentSignature: { type: String, required: true }, // Path or URL
});

module.exports = mongoose.model('FormData', FormDataSchema);
