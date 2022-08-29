#include <SPI.h>
#include <MFRC522.h>

constexpr uint8_t RST_PIN = 9;
constexpr uint8_t SS_PIN = 10;

//setuing up global variables
String data ="";
char  state = 'f';
bool stringComplete = false;

//RFID variables


MFRC522 mfrc522(SS_PIN, RST_PIN); // intiating a mfrc522 instance

void setup() {
  // put your setup code here, to run once:
 
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  data.reserve(200); // reserving 200 bytes for the string buffer that will take up the long string of tasks
  // limitations for the string being sent are real and have to be considered when testing it out.
  SPI.begin();
  mfrc522.PCD_Init();
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH); // indicator that the code is running. The life light of the arduino. An off light means that the code is broken

  if(stringComplete){
    state = data[0];//designate the state
    Serial.println(state);
    
    stringComplete = false;
    digitalWrite(LED_BUILTIN, LOW);
    delay(2000); // 2 seconds off to show that the code reaches this part.
    
    
    shorten();
    
    if(state == '1'){//write content of data into card
      
      writeToCard();
      delay(2000); 
      
      Serial.println("done");
        
      }
    
    else if(state == '2'){
      //read the content of the card and send it as a long String to python  
      
      Serial.println("reached");
      readCard();
      delay(2000);
  
    }

    data = "";
    state = '5';
  
  }

}


void serialEvent(){ // only runs when there is bytes availabel on the input buffer
  while(Serial.available()){
    digitalWrite(LED_BUILTIN, LOW);
    char inChar = (char)Serial.read();
    data += inChar;

    if(inChar == '^'){
       stringComplete = true;
     }
    
  }
  
}

void shorten(){ //delets the first and last characters of the string as these two are only indicators and not data to save
  String finalData = "";
  for(int i =1; i < data.length() ; i++){
    finalData += data[i];
    }
  data = finalData;
  }

void writeToCard(){
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("keep card close to reader");
     
  
  while( ! mfrc522.PICC_IsNewCardPresent()) {}
  Serial.println("passed");
      // Select one of the cards
  while ( ! mfrc522.PICC_ReadCardSerial()) {}

  Serial.println("card detected, saving to card");

  
  //calculate amount of 16 bytes bloks to use
  byte block =1;
  byte trailerBlock = 3;

  //Serial.println(data.length());
  int AoB = (data.length() -1)/16;
  if((AoB % 16)> 0) {AoB++;}
  
  
  //separate the string into 16 bytes and write to card, one by one
  int counter = 16;
  int start = 0;
  for(int i = 0;i< AoB;i++){
    
    String subString;
    subString = data.substring(start, counter);
    Serial.println(subString);
    counter = counter + 16;
    start = start +16;
    if (block > 2 && (block + 1) % 4 == 0) {
      block += 1;  //avoid writting in any trailer of a sector.
      trailerBlock += 4;
    }
   
    
  



    
    MFRC522::MIFARE_Key key;
     
    for(byte i =0; i < 6;i++) key.keyByte[i]= 0xFF;
     
    byte buffer[18];
  
    MFRC522::StatusCode status;
    
    subString.getBytes(buffer, 18);
    
    status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(mfrc522.uid)); //problem starts here
    //Serial.println(AoB);  
    if (status != MFRC522::STATUS_OK) {
      //Serial.print(F("PCD_Authenticate() failed: "));
      //Serial.println(mfrc522.GetStatusCodeName(status));
      return;
    }
    //else Serial.println(F("PCD_Authenticate() success: "));
  
    // Write block
    status = mfrc522.MIFARE_Write(block, buffer, 16);
    if (status != MFRC522::STATUS_OK) {
      //Serial.print(F("MIFARE_Write() failed: "));
      //Serial.println(mfrc522.GetStatusCodeName(status));
      return;
    }
    //else Serial.println(F("MIFARE_Write() success: "));
    delay(1000);
    block++;
  }
   // Halt PICC
  mfrc522.PICC_HaltA();
  // Stop encryption on PCD
  mfrc522.PCD_StopCrypto1();
  digitalWrite(LED_BUILTIN, LOW);
}
  
void readCard() {
  digitalWrite(LED_BUILTIN, HIGH);

  Serial.println("keep card close to reader");
     
  
  while( ! mfrc522.PICC_IsNewCardPresent()) {}

      // Select one of the cards
  while ( ! mfrc522.PICC_ReadCardSerial()) {}

  Serial.println("reading card...");
  String data;
  data = "^";
  byte block =1;
  byte trailerBlock = 3;

  
  while (true){
    boolean condition = false;
    MFRC522::MIFARE_Key key;
    for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
    
    byte len;
    MFRC522::StatusCode status;
    
    
    byte  buffer1[18];
    len = 18;
    int start = start +16;
    if (block > 2 && (block + 1) % 4 == 0) {
      block += 1;  //avoid writting in any trailer of a sector.
      trailerBlock += 4;
    }
    
    status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid)); //line 834 of MFRC522.cpp file
    if (status != MFRC522::STATUS_OK) {
      Serial.print(F("Authentication failed: "));
      Serial.println(mfrc522.GetStatusCodeName(status));
      return;
    }
  
    status = mfrc522.MIFARE_Read(block, buffer1, &len);
    if (status != MFRC522::STATUS_OK) {
      Serial.print(F("Reading failed: "));
      Serial.println(mfrc522.GetStatusCodeName(status));
      return;
    }
    
    for (uint8_t i = 0; i < 16; i++){
      data += (char)buffer1[i];
      
      if (buffer1[i] == 94){
         condition = true;
         break;
        }
    }
    
    

    
    if (condition == true){
      Serial.println(data);
      break;}
    Serial.println(data);
    
    block = block + 1;
    delay(1000);
  }
  
  
  // Halt PICC
  mfrc522.PICC_HaltA();
  // Stop encryption on PCD
  mfrc522.PCD_StopCrypto1();
  digitalWrite(LED_BUILTIN, LOW);
  return 1;


  
}
