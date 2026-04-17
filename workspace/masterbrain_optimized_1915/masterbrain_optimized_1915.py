# Dre Proprietary
# Copyright (c) 2023 Dre Proprietary. All rights reserved.
# This software is the confidential and proprietary information of Dre Proprietary.
# ("Confidential Information"). You shall not disclose such Confidential Information and shall use it only in accordance with the terms of the license agreement you entered into with Dre Proprietary.

import logging
from datetime import datetime
from typing import Dict, List

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ElderlyCarePatient:
    """
    Represents an elderly care patient.

    Attributes:
        patient_id (int): Unique patient identifier.
        name (str): Patient name.
        age (int): Patient age.
        medical_history (Dict[str, str]): Patient medical history.
    """

    def __init__(self, patient_id: int, name: str, age: int, medical_history: Dict[str, str]):
        """
        Initializes an ElderlyCarePatient object.

        Args:
            patient_id (int): Unique patient identifier.
            name (str): Patient name.
            age (int): Patient age.
            medical_history (Dict[str, str]): Patient medical history.
        """
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.medical_history = medical_history

    def __str__(self):
        """
        Returns a string representation of the patient.

        Returns:
            str: Patient details.
        """
        return f"Patient ID: {self.patient_id}, Name: {self.name}, Age: {self.age}, Medical History: {self.medical_history}"


class ElderlyCareSystem:
    """
    Represents an elderly care system.

    Attributes:
        patients (List[ElderlyCarePatient]): List of patients in the system.
    """

    def __init__(self):
        """
        Initializes an ElderlyCareSystem object.
        """
        self.patients = []

    def add_patient(self, patient: ElderlyCarePatient):
        """
        Adds a patient to the system.

        Args:
            patient (ElderlyCarePatient): Patient to add.
        """
        try:
            self.patients.append(patient)
            logger.info(f"Patient {patient.name} added to the system.")
        except Exception as e:
            logger.error(f"Error adding patient: {str(e)}")

    def remove_patient(self, patient_id: int):
        """
        Removes a patient from the system.

        Args:
            patient_id (int): ID of the patient to remove.
        """
        try:
            patient_to_remove = next((patient for patient in self.patients if patient.patient_id == patient_id), None)
            if patient_to_remove:
                self.patients.remove(patient_to_remove)
                logger.info(f"Patient with ID {patient_id} removed from the system.")
            else:
                logger.warning(f"Patient with ID {patient_id} not found in the system.")
        except Exception as e:
            logger.error(f"Error removing patient: {str(e)}")

    def get_patient(self, patient_id: int) -> ElderlyCarePatient:
        """
        Retrieves a patient from the system.

        Args:
            patient_id (int): ID of the patient to retrieve.

        Returns:
            ElderlyCarePatient: Patient with the specified ID, or None if not found.
        """
        try:
            return next((patient for patient in self.patients if patient.patient_id == patient_id), None)
        except Exception as e:
            logger.error(f"Error retrieving patient: {str(e)}")
            return None


def main():
    # Create an instance of the elderly care system
    elderly_care_system = ElderlyCareSystem()

    # Create patients
    patient1 = ElderlyCarePatient(1, "John Doe", 75, {"condition": "diabetes", "medication": "insulin"})
    patient2 = ElderlyCarePatient(2, "Jane Doe", 80, {"condition": "hypertension", "medication": "beta blockers"})

    # Add patients to the system
    elderly_care_system.add_patient(patient1)
    elderly_care_system.add_patient(patient2)

    # Retrieve a patient from the system
    retrieved_patient = elderly_care_system.get_patient(1)
    if retrieved_patient:
        logger.info(f"Retrieved patient: {retrieved_patient}")
    else:
        logger.warning("Patient not found in the system.")

    # Remove a patient from the system
    elderly_care_system.remove_patient(2)


if __name__ == "__main__":
    main()