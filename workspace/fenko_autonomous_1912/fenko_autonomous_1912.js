/**
 * Dre Proprietary
 *
 * Copyright (c) 2023 Dre Proprietary, Inc.
 */

// Import necessary modules and dependencies
import { log } from './logging.js';
import { validateInput } from './validation.js';

/**
 * fenko_autonomous_1912.js - High-performance tool for Micro-SaaS Productivity Utilities
 *
 * This module provides a suite of functions to enhance productivity in SaaS environments.
 */

/**
 * Function to initialize the autonomous utility system.
 * @param {Object} config - Configuration object containing settings and parameters.
 */
function initAutonomousUtilitySystem(config) {
    try {
        // Validate input configuration
        validateInput(config);

        log.info('Initializing autonomous utility system with provided configuration.');

        // Initialize core components based on configuration
        const coreComponents = initializeCoreComponents(config);
        
        // Start the utility processes
        startUtilityProcesses(coreComponents);

        log.info('Autonomous utility system initialized successfully.');
    } catch (error) {
        log.error(`Failed to initialize autonomous utility system: ${error.message}`);
        throw error;
    }
}

/**
 * Function to initialize core components of the utility system.
 * @param {Object} config - Configuration object containing settings and parameters.
 * @returns {Array} - Array of initialized core components.
 */
function initializeCoreComponents(config) {
    // Initialize core components based on configuration
    const coreComponents = [];

    if (config.enableDataProcessing) {
        coreComponents.push(processData(config.dataProcessingConfig));
    }

    if (config.enableTaskAutomation) {
        coreComponents.push(automateTasks(config.taskAutomationConfig));
    }

    return coreComponents;
}

/**
 * Function to start utility processes.
 * @param {Array} coreComponents - Array of initialized core components.
 */
function startUtilityProcesses(coreComponents) {
    try {
        for (const component of coreComponents) {
            if (component.start) {
                log.info(`Starting ${component.name} process.`);
                component.start();
            }
        }

        log.info('All utility processes started successfully.');
    } catch (error) {
        log.error(`Failed to start utility processes: ${error.message}`);
        throw error;
    }
}

/**
 * Function to process data based on configuration.
 * @param {Object} config - Configuration object for data processing.
 * @returns {Object} - Data processing component instance.
 */
function processData(config) {
    // Initialize and return a data processing component
    const dataProcessor = new DataProcessor(config);
    log.info('Data processor initialized.');
    return dataProcessor;
}

/**
 * Function to automate tasks based on configuration.
 * @param {Object} config - Configuration object for task automation.
 * @returns {Object} - Task automation component instance.
 */
function automateTasks(config) {
    // Initialize and return a task automation component
    const taskAutomator = new TaskAutomator(config);
    log.info('Task automator initialized.');
    return taskAutomator;
}

// Export the main function for use in other modules
export { initAutonomousUtilitySystem };