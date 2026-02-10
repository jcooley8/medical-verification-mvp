import type { ExtractionResult } from '../types/extraction.types';

// Mock data for testing the click-to-verify feature
export const mockExtractionData: ExtractionResult = {
  document_id: 'mock-doc-123',
  pdf_url: '', // Add a PDF to public/ folder for full demo
  total_pages: 10,
  chronology: [
    {
      date: '2023-10-15',
      provider: 'Dr. Sarah Smith',
      facility: 'General Hospital',
      event_type: 'Initial Consultation',
      description: 'Patient reports severe headaches lasting 2 weeks. Pain rated 8/10, predominantly frontal. No visual disturbances noted.',
      source_refs: [
        {
          field: 'date',
          page_number: 1,
          bounding_box: {
            left: 0.15,
            top: 0.25,
            width: 0.2,
            height: 0.03,
          },
          confidence: 0.98,
          text: '2023-10-15',
        },
        {
          field: 'provider',
          page_number: 1,
          bounding_box: {
            left: 0.15,
            top: 0.30,
            width: 0.25,
            height: 0.03,
          },
          confidence: 0.95,
          text: 'Dr. Sarah Smith',
        },
        {
          field: 'description',
          page_number: 1,
          bounding_box: {
            left: 0.15,
            top: 0.40,
            width: 0.70,
            height: 0.10,
          },
          confidence: 0.92,
          text: 'Patient reports severe headaches...',
        },
      ],
    },
    {
      date: '2023-10-19',
      provider: 'Dr. Michael Jones',
      facility: 'Radiology Center',
      event_type: 'MRI Scan',
      description: 'Brain MRI with and without contrast. No abnormalities detected. Normal brain parenchyma and ventricles.',
      source_refs: [
        {
          field: 'date',
          page_number: 3,
          bounding_box: {
            left: 0.15,
            top: 0.20,
            width: 0.2,
            height: 0.03,
          },
          confidence: 0.99,
          text: '2023-10-19',
        },
        {
          field: 'provider',
          page_number: 3,
          bounding_box: {
            left: 0.15,
            top: 0.24,
            width: 0.25,
            height: 0.03,
          },
          confidence: 0.96,
          text: 'Dr. Michael Jones',
        },
        {
          field: 'description',
          page_number: 3,
          bounding_box: {
            left: 0.15,
            top: 0.35,
            width: 0.70,
            height: 0.08,
          },
          confidence: 0.94,
          text: 'Brain MRI with and without contrast...',
        },
      ],
    },
    {
      date: '2023-10-22',
      provider: 'Dr. Sarah Smith',
      facility: 'General Hospital',
      event_type: 'Follow-up Visit',
      description: 'Patient reports improvement with prescribed medication. Headaches reduced to 3/10 severity. Continue current treatment plan.',
      source_refs: [
        {
          field: 'date',
          page_number: 5,
          bounding_box: {
            left: 0.15,
            top: 0.18,
            width: 0.2,
            height: 0.03,
          },
          confidence: 0.97,
          text: '2023-10-22',
        },
        {
          field: 'description',
          page_number: 5,
          bounding_box: {
            left: 0.15,
            top: 0.30,
            width: 0.70,
            height: 0.12,
          },
          confidence: 0.89,
          text: 'Patient reports improvement...',
        },
      ],
    },
  ],
  bills: [
    {
      cpt_code: '99214',
      description: 'Office or other outpatient visit, 30-39 minutes',
      quantity: 1,
      unit_price: 250.00,
      total: 250.00,
      date_of_service: '2023-10-15',
      source_refs: [
        {
          field: 'cpt_code',
          page_number: 7,
          bounding_box: {
            left: 0.10,
            top: 0.35,
            width: 0.15,
            height: 0.025,
          },
          confidence: 0.99,
          text: '99214',
        },
        {
          field: 'total',
          page_number: 7,
          bounding_box: {
            left: 0.75,
            top: 0.35,
            width: 0.15,
            height: 0.025,
          },
          confidence: 0.98,
          text: '$250.00',
        },
      ],
    },
    {
      cpt_code: '70553',
      description: 'MRI Brain with and without contrast',
      quantity: 1,
      unit_price: 1850.00,
      total: 1850.00,
      date_of_service: '2023-10-19',
      source_refs: [
        {
          field: 'cpt_code',
          page_number: 7,
          bounding_box: {
            left: 0.10,
            top: 0.40,
            width: 0.15,
            height: 0.025,
          },
          confidence: 0.96,
          text: '70553',
        },
        {
          field: 'total',
          page_number: 7,
          bounding_box: {
            left: 0.75,
            top: 0.40,
            width: 0.15,
            height: 0.025,
          },
          confidence: 0.97,
          text: '$1,850.00',
        },
      ],
    },
    {
      cpt_code: '99213',
      description: 'Office or other outpatient visit, 20-29 minutes',
      quantity: 1,
      unit_price: 150.00,
      total: 150.00,
      date_of_service: '2023-10-22',
      source_refs: [
        {
          field: 'cpt_code',
          page_number: 7,
          bounding_box: {
            left: 0.10,
            top: 0.45,
            width: 0.15,
            height: 0.025,
          },
          confidence: 0.78,  // Low confidence for testing
          text: '99213',
        },
        {
          field: 'total',
          page_number: 7,
          bounding_box: {
            left: 0.75,
            top: 0.45,
            width: 0.15,
            height: 0.025,
          },
          confidence: 0.95,
          text: '$150.00',
        },
      ],
    },
  ],
};
