#include <Grove_LCD_RGB_Backlight.h>
#include <TM1637Display.h>
//#include <string>

const int joystickXPin = A0;
const int joystickYPin = A1;

const int displayClkPin = D7;
const int displayDIOPin = D10;

const int led1 = D4;
const int led2 = D3;

String question1 = "When was the first bombe built at Bletchley Park?";
int scrollPosition = 0;
int messageLength = 49;
const int scrollDelay = 500;
unsigned long previousMillis = 0;

const int yearBuilt = 1940;
const int morseCodeNumber = 4391;

int joystickXValue;
int joystickYValue;

// Create an instance of the display
rgb_lcd lcd;
TM1637Display display(displayClkPin, displayDIOPin);

// Initialize variables
int digits[4] = {0, 0, 0, 0};
int digits2[4] = {0, 0, 0, 0};
int currentDigitIndex = 0;

unsigned long lastMoveTime = 0;
const unsigned long debounceDelay = 200; // 200 milliseconds debounce delay
const int deadzone = 800;                // Deadzone for joystick

void setup() {
  Serial.begin(9600);
  delay(1000);

  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  display.setBrightness(0x0a);

  // Initialize the display
  lcd.begin(16, 2); // 16 columns, 2 rows

  // Set the RGB backlight color (red, green, blue)
  lcd.setRGB(255, 255, 255); // White backlight
  display.setBrightness(0x0f);
  lcd.print(question1.substring(scrollPosition, scrollPosition + 16));

  pinMode(joystickXPin, INPUT);
  pinMode(joystickYPin, INPUT);

  display.showNumberDec(digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 +
                        digits[3]);
}

void loop() {
  int numberToShow = 0;
  joystickXValue = analogRead(joystickXPin);
  joystickYValue = analogRead(joystickYPin);
  unsigned long currentMillis = millis();

  checkNumber();

  // Display the updated number
  numberToShow =
      digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3];
  display.showNumberDec(numberToShow);

  if (numberToShow == yearBuilt) {
    Serial.println("number is equal to year built");
    lcd.clear();
    lcd.print("First letter: J");
    delay(5000);
    lcd.clear();
    lcd.print("Morse code");
    Serial.println("Printed on LCD");
    delay(1000);
    four();
    Serial.println("Morse code function four executed");
    delay(2000);
    three();
    delay(2000);
    nine();
    delay(2000);
    one();
    delay(2000);
  }

  if (currentMillis - previousMillis >= scrollDelay) {
    previousMillis = currentMillis;
    scrollPosition++;
    if (scrollPosition > messageLength - 16) {
      scrollPosition =
          0; // Reset scroll position when end of message is reached
    }
    Serial.println("lcd.clear begin");
    lcd.clear();
    lcd.setCursor(0, 1); // Set cursor to beginning of second line
    lcd.print(question1.substring(scrollPosition, scrollPosition + 16));
    Serial.println("Past lcd.clear()");
  }
}

void checkNumber() {
  unsigned long currentTime = millis();
  // Handle horizontal (left/right) movement to switch digits
  if (currentTime - lastMoveTime > debounceDelay) {
    if (joystickXValue > (2048 + deadzone)) { // Left
      currentDigitIndex = (currentDigitIndex - 1 + 4) % 4;
      lastMoveTime = currentTime;
    } else if (joystickXValue < (2048 - deadzone)) { // Right
      currentDigitIndex = (currentDigitIndex + 1) % 4;
      lastMoveTime = currentTime;
    }

    // Handle vertical (up/down) movement to increment/decrement digits
    if (joystickYValue < (2048 - deadzone)) { // Up
      digits[currentDigitIndex] = (digits[currentDigitIndex] + 1) % 10;
      lastMoveTime = currentTime;
    } else if (joystickYValue > (2048 + deadzone)) { // Down
      digits[currentDigitIndex] = (digits[currentDigitIndex] - 1 + 10) % 10;
      lastMoveTime = currentTime;
    }
  }
}

void shortBuzz() {
  digitalWrite(led1, HIGH);
  digitalWrite(led2, HIGH);
  delay(500); // Leave it on for 0.5 second
  digitalWrite(led1, LOW);
  digitalWrite(led2, LOW);
  delay(500); // Wait 0.5 second
}

void longBuzz() {
  digitalWrite(led1, HIGH);
  digitalWrite(led2, HIGH);
  delay(2000); // Leave it on for 2 seconds
  digitalWrite(led1, LOW);
  digitalWrite(led2, LOW);
  delay(500); // Wait 0.5 second
}

void one() {
  shortBuzz();
  delay(1000);
  longBuzz();
  delay(1000);
  longBuzz();
  delay(1000);
  longBuzz();
  delay(1000);
  longBuzz();
  delay(1000);
}

void four() {
  shortBuzz();
  delay(1000);
  shortBuzz();
  delay(1000);
  shortBuzz();
  delay(1000);
  shortBuzz();
  delay(1000);
  longBuzz();
  delay(1000);
}

void nine() {
  longBuzz();
  delay(1000);
  longBuzz();
  delay(1000);
  longBuzz();
  delay(1000);
  longBuzz();
  delay(1000);
  shortBuzz();
  delay(1000);
}

void three() {
  shortBuzz();
  delay(1000);
  shortBuzz();
  delay(1000);
  shortBuzz();
  delay(1000);
  longBuzz();
  delay(1000);
  longBuzz();
  delay(1000);
}
