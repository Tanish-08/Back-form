const express = require('express');
const mongoose = require('mongoose');
const multer = require('multer');
const bodyParser = require('body-parser');
const FormData = require('./models/FormData'); // Import the schema
const path = require('path');
require('dotenv').config();


const app = express();
const PORT = 3000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Static directory for file uploads
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('Connected to MongoDB'))
.catch((err) => console.error('Error connecting to MongoDB:', err));


// Multer setup for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, `${Date.now()}-${file.originalname}`);
  },
});

const upload = multer({ storage });

// API Endpoint to handle form submission
app.post(
  '/submit-form',
  upload.fields([
    { name: 'fee_receipt_file', maxCount: 1 },
    { name: 'student_signature', maxCount: 1 },
  ]),
  async (req, res) => {
    try {
      const formData = new FormData({
        department: req.body.department,
        name: req.body.name,
        fatherName: req.body.father_name,
        enrollNo: req.body['enroll_no.'],
        programName: req.body.program_name,
        semesterBatch: req.body.semester_batch,
        email: req.body.email,
        feeReceiptNo: req.body.fee_receipt_no,
        amount: req.body.amount,
        feeReceiptFile: req.files['fee_receipt_file'][0].path,
        backPaper: req.body.back_semester
          ? req.body.back_semester.map((semester, index) => ({
              semester,
              courseCode: req.body.back_course_code[index],
              courseName: req.body.back_course_name[index],
            }))
          : [],
        repeatCourse: req.body.repeat_semester
          ? req.body.repeat_semester.map((semester, index) => ({
              semester,
              courseCode: req.body.repeat_course_code[index],
              courseName: req.body.repeat_course_name[index],
            }))
          : [],
        date: req.body.date,
        studentSignature: req.files['student_signature'][0].path,
      });

      // Save data to MongoDB
      await formData.save();
      res.status(200).send({ message: 'Form submitted successfully!' });
    } catch (error) {
      console.error(error);
      res.status(500).send({ message: 'Internal server error.' });
    }
  }
);

// Start the server
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));