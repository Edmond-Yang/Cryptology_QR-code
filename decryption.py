from method import PlaintextToHexSecretSharer
import inquirer
import animation
import cv2
from pyzbar import pyzbar


def capture():

    # 初始化攝影機
    cap = cv2.VideoCapture(0)

    # 初始化QR code檢測器
    detector = cv2.QRCodeDetector()

    while True:
        # 讀取當前幀
        _, img = cap.read()

        # 檢測QR code
        data, bbox, _ = detector.detectAndDecode(img)

        # 如果有檢測到QR code
        if data:
            break

    # 釋放資源
    cap.release()
    cv2.destroyAllWindows()

    return data


def main():

    # Enter shares

    shares = []

    while True:
        questions = [
            inquirer.List('share',
                        message='Next Share',
                        choices=['Use Camera to Scan QR-code', 'Use QR-code Image',
                                 'Use Text', 'Edit The Share', 'I don\'t have another one'],
                    ),
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)['share']

        if answer == 'I don\'t have another one' and shares:
            break
        elif answer == 'Use Text':
            txt = input('Enter your share: ')
            if txt:
                shares.append(txt)
            else:
                print('You don\'t input any text')
        elif answer == 'Use QR-code Image':
            txt = input('Enter Your Image Path: ')
            if txt:
                try:
                    image = cv2.imread(txt)
                    share = pyzbar.decode(image)[0].data.decode('utf-8')
                    questions = [
                        inquirer.List('confirm',
                                      message=f'Confirm Your Share: {share}',
                                      choices=['Yes', 'No'],
                        ),
                    ]
                    answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)['confirm']
                    if answer == 'Yes':
                        shares.append(share)

                except:
                    print('Error Occur. Please Try Again')
            else:
                print('You don\'t input any text')
        elif answer == 'Use Camera to Scan QR-code':

            wait = animation.Wait('spinner', 'Scanning QR-code.. It may take a while.. ')
            wait.start()
            try:
                share = capture()
                wait.stop()
                questions = [
                    inquirer.List('confirm',
                                  message=f'Confirm Your Share: {share}',
                                  choices=['Yes', 'No'],
                    ),
                ]
                answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)['confirm']
                if answer == 'Yes':
                    shares.append(share)
            except:
                wait.stop()
                print('Error Occur. You should accept privacy for camera.')
            pass
        elif answer == 'Edit The Share':
            questions = [
                inquirer.List('confirm',
                              message=f'Delete Your Share:',
                              choices= shares + ['Delete All Above', 'Do Nothing'],
                              ),
            ]
            answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)['confirm']
            if answer == 'Delete All Above':
                shares = []
            elif answer == 'Do Nothing':
                pass
            elif answer in shares:
                shares.remove(answer)

        else:
            print('Error Occur.')

    # Recover
    wait = animation.Wait('spinner', 'Generating randomness.. It may take a while.. ')
    wait.start()
    message = PlaintextToHexSecretSharer.recover_secret(shares)
    wait.stop()
    print('Original message:\n'+message)


if __name__ == '__main__':
    main()
