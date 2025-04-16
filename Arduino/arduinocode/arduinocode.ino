#include <FastLED.h>

#define NUM_LEDS 15  // Total number of LEDs (3 LEDs per joint for 5 joints)
#define DATA_PIN 3    // Pin where the LED strip is connected

CRGB leds[NUM_LEDS];  // Array to hold the LED colors

// Function prototypes
void decodeSerialInput(String input);
void moveJoints(int jointAngles[5]);
void setLEDs(int jointColors[5][3]);
void verifyLEDs();  // Function to verify LED strip functionality
void hexToRGB(String hexColor, int &r, int &g, int &b);

void setup() {
    Serial.begin(9600);  // Start serial communication
    FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);  // Initialize the LED strip

    // Verify LED strip functionality
    verifyLEDs();
}

void loop() {
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');  // Read the incoming serial data
        Serial.print("Received: ");  // Debugging output
        Serial.println(input);  // Print the received input
        decodeSerialInput(input);  // Decode the input
    }
}

// Function to verify LED strip functionality
void verifyLEDs() {
    // Cycle through colors to verify the LED strip
    for (int i = 0; i < 256; i++) {
        for (int j = 0; j < NUM_LEDS; j++) {
            leds[j] = CHSV(i, 255, 255);  // Set color using HSV
        }
        FastLED.show();  // Update the LED strip
        delay(10);  // Delay to see the color change
    }

    // Turn off the LEDs after verification
    for (int j = 0; j < NUM_LEDS; j++) {
        leds[j] = CRGB::Black;  // Turn off all LEDs
    }
    FastLED.show();  // Update the LED strip
}

// Function to decode the serial input
void decodeSerialInput(String input) {
    int armNumber;
    int jointAngles[5];
    int jointColors[5][3];  // Array to hold RGB values for each joint

    // Example input format: $2:90:#FF5500:90:#55FFFF:90:#000000:90:#000000:90:#000000
    // Split the input by ':'
    int index = 0;
    char* token = strtok(input.c_str(), ":");
    
    // Check if the first character is '$' and move to the next token
    if (token != NULL && token[0] == '$') {
        token = strtok(NULL, ":");  // Move to the arm number token
    }

    // Now parse the arm number
    if (token != NULL) {
        armNumber = atoi(token);  // Get the arm number
        Serial.print("Parsed Arm Number: ");  // Debugging output
        Serial.println(armNumber);  // Print the parsed arm number
    }

    // Continue parsing joint angles and colors
    while (token != NULL) {
        if (index % 2 == 1) {
            jointAngles[index / 2] = atoi(token);  // Get joint angles
        } else {
            // Get joint colors
            String colorStr = token;
            int r, g, b;
            hexToRGB(colorStr, r, g, b);
            jointColors[index / 2][0] = r; // R
            jointColors[index / 2][1] = g; // G
            jointColors[index / 2][2] = b; // B
        }
        token = strtok(NULL, ":");
        index++;
    }

    // Only process if the arm number is 2
    if (armNumber == 2) {
        // Move joints and set LEDs based on the decoded values
        moveJoints(jointAngles);
        setLEDs(jointColors);

        // Send joint angles and colors via serial
        for (int i = 0; i < 5; i++) {
            Serial.print("Joint ");
            Serial.print(i + 1);
            Serial.print(": ");
            Serial.print(jointAngles[i]);
            Serial.print(" - ");
            Serial.print(jointColors[i][0]);
            Serial.print(".");
            Serial.print(jointColors[i][1]);
            Serial.print(".");
            Serial.println(jointColors[i][2]);
        }
    } else {
        Serial.println("Received data for Arm 1, ignoring.");  // Debugging output for ignored data
    }
}

// Function to move joints (currently a placeholder)
void moveJoints(int jointAngles[5]) {
    // Implement joint movement logic here
    // For example, you could use servo motors to move the joints based on the angles
}

// Function to set the LED colors based on joint colors
void setLEDs(int jointColors[5][3]) {
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 3; j++) {
            int ledIndex = i * 3 + j;  // Calculate the LED index for each joint
            leds[ledIndex] = CRGB(jointColors[i][0], jointColors[i][1], jointColors[i][2]);  // Set LED color
        }
    }
    FastLED.show();  // Update the LED strip
}

// Function to convert hex color to RGB
void hexToRGB(String hexColor, int &r, int &g, int &b) {
    // Remove the '#' character if present
    if (hexColor.charAt(0) == '#') {
        hexColor.remove(0, 1);
    }

    // Convert hex to RGB
    r = strtol(hexColor.substring(0, 2).c_str(), NULL, 16); // Red
    g = strtol(hexColor.substring(2, 4).c_str(), NULL, 16); // Green
    b = strtol(hexColor.substring(4, 6).c_str(), NULL, 16); // Blue
}
