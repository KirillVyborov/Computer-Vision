import cv2
import numpy as np

WINDOW_NAME = "Нажмите 4 точки (по часовой), 'r' - сброс, 'q' - выход"

def on_mouse(event, x, y, flags, param):
    pts = param['pts']
    img = param['img']
    disp = img.copy()
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(pts) < 4:
            pts.append((x, y))
    for i, p in enumerate(pts):
        cv2.circle(disp, p, 5, (0, 0, 255), -1)
        cv2.putText(disp, str(i+1), (p[0]+6, p[1]+6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    cv2.imshow(WINDOW_NAME, disp)

def interactive_warp(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Изображение не найдено: {img_path}")

    param = {'pts': [], 'img': img}
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse, param)

    while True:
        disp = img.copy()
        for i, p in enumerate(param['pts']):
            cv2.circle(disp, p, 5, (0, 0, 255), -1)
            cv2.putText(disp, str(i+1), (p[0]+6, p[1]+6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
        cv2.imshow(WINDOW_NAME, disp)
        key = cv2.waitKey(20) & 0xFF
        if key == ord('r'):
            param['pts'].clear()
            print("Сброс точек.")
        elif key == ord('q') or key == 27:
            break
        if len(param['pts']) == 4:
            src = np.array(param['pts'], dtype=np.float32)
            widthA = np.linalg.norm(src[0] - src[1])
            widthB = np.linalg.norm(src[3] - src[2])
            maxWidth = int(max(widthA, widthB))
            heightA = np.linalg.norm(src[0] - src[3])
            heightB = np.linalg.norm(src[1] - src[2])
            maxHeight = int(max(heightA, heightB))

            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]
            ], dtype=np.float32)

            H = cv2.getPerspectiveTransform(src, dst)
            warped = cv2.warpPerspective(img, H, (maxWidth, maxHeight))
            cv2.imshow("Неверный результат", warped)

            print("Нажмите 's' для сохранения, 'r' для сброса точек, 'q' для выхода.")
            k = cv2.waitKey(0) & 0xFF
            if k == ord('s'):
                cv2.imwrite("corrected.png", warped)
                print("Сохранено как 'corrected.png'.")
            if k == ord('r'):
                param['pts'].clear()
                cv2.destroyWindow("Неверный результат")
            else:
                pass

    cv2.destroyAllWindows()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Исправление изображения")
    parser.add_argument("image", help="Путь к изображению")
    args = parser.parse_args()
    interactive_warp(args.image)