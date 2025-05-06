from astropy.coordinates import Galactic, ICRS, GeocentricMeanEcliptic, get_sun, get_body, EarthLocation, AltAz
from astropy.time import Time
from astropy import units as u




from .zodiac import *
from .airglow import *
from .transparency import *
from .airglow_spectrum import *
from .modtran_default_kp_transparency import *
from .solar_spectrum import *
from .band_V_data import *
from .solar_radio_flux import *
from .star_catalogues import *
from .albedo_of_planets import *
from .planets import *

def galactic_to_equatorial(l, b):
    """
    Преобразует галактические координаты в эклиптические.

    Функция принимает галактическую долготу и широту объекта, преобразует их 
    в эклиптические координаты (долготу и широту) с использованием стандартной 
    эпохи J2000.0 и библиотеки `astropy`.

    Параметры:
        l (float): Галактическая долгота объекта (в градусах).
        b (float): Галактическая широта объекта (в градусах).

    Возвращает:
        tuple: Кортеж из двух значений:
            - ecl_lon (float): Эклиптическая долгота объекта (в градусах).
            - ecl_lat (float): Эклиптическая широта объекта (в градусах).

    Примечания:
        - Для преобразования используется библиотека `astropy`:
            - `Galactic`: Представляет галактические координаты.
            - `GeocentricMeanEcliptic`: Представляет эклиптические координаты.
        - Эпоха расчетов фиксирована как J2000.0.
        - Результат возвращается в градусах, так как это наиболее распространенный формат для астрономических данных.

    Зависимости:
        - `astropy.units`: Для работы с единицами измерения (градусы).
        - `astropy.time.Time`: Для задания эпохи J2000.0.
        - `astropy.coordinates.Galactic`: Для представления галактических координат.
        - `astropy.coordinates.GeocentricMeanEcliptic`: Для представления эклиптических координат.
    """
    import astropy.units as u
# Входные данные: галактические координаты и эпоха
    galactic_l = l * u.deg  # Галактическая долгота
    galactic_b = b * u.deg # Галактическая широта
    epoch = Time('J2000.0')  # Эпоха (стандартная для астрономических расчетов)

    # Создаем объект галактических координат
    galactic_coords = Galactic(l=galactic_l, b=galactic_b)

    # Преобразуем галактические координаты в экваториальные (ICRS)
    ecliptic_coords = galactic_coords.transform_to(GeocentricMeanEcliptic(equinox=epoch))


#     print("Техническая проверка")
#     print(f"Эклиптическая долгота (λ): {ecliptic_coords.lon.to(u.deg)}")
#     print(f"Эклиптическая широта (β): {ecliptic_coords.lat.to(u.deg)}")
    
    ecl_lon = ecliptic_coords.lon.to(u.deg).value
    ecl_lat = ecliptic_coords.lat.to(u.deg).value
    return(ecl_lon, ecl_lat)

def Sun_ecl_lon(date, time):
    """
    Вычисляет эклиптическую долготу Солнца по заданным дате и времени.

    Функция принимает дату и время наблюдения, использует библиотеку `astropy` 
    для расчета положения Солнца в геоцентрической эклиптической системе координат 
    и возвращает эклиптическую долготу Солнца.

    Параметры:
        date (str): Дата наблюдения в формате 'YYYY-MM-DD' (например, '2023-11-03').
        time (str): Время наблюдения в формате 'HH:MM:SS' (например, '12:00:00').

    Возвращает:
        ecl_lon_of_Sun (float): Эклиптическая долгота Солнца (в градусах).

    Примечания:
        - Для расчетов используется библиотека `astropy`:
            - `get_sun`: Получает положение Солнца в геоцентрической системе координат.
            - `GeocentricMeanEcliptic`: Преобразует координаты в эклиптическую систему.
        - Результат возвращается в градусах, так как это наиболее распространенный формат 
          для астрономических данных.
        - Эклиптическая широта Солнца не возвращается, так как она не используется в дальнейших расчетах.

    Зависимости:
        - `astropy.time.Time`: Для обработки даты и времени.
        - `astropy.coordinates.get_sun`: Для получения положения Солнца.
        - `astropy.coordinates.GeocentricMeanEcliptic`: Для преобразования координат 
          в эклиптическую систему.
    """
    datetime = date + ' ' + time
    observation_time = Time(datetime)

    # Получаем координаты Солнца в геоцентрической системе координат
    sun_position = get_sun(observation_time)

    # Преобразуем координаты Солнца в эклиптическую систему (геоцентрическую)
    ecliptic_coords = sun_position.transform_to(GeocentricMeanEcliptic())

    # Извлекаем эклиптическую долготу (lon) и широту (lat)
    ecliptic_longitude = ecliptic_coords.lon
    ecliptic_latitude = ecliptic_coords.lat

    # Выводим результат
#     print("Техническая проверка:")
#     print(f"Эклиптическая долгота Солнца: {ecliptic_longitude}")
#     print(f"Эклиптическая широта Солнца: {ecliptic_latitude}")
    ecl_lon_of_Sun = ecliptic_longitude.value
    return(ecl_lon_of_Sun)

def sum_of_spectrums(array_1, meaning_1, array_2, meaning_2):
    """
    Универсальная функция для суммы двух спектров по совпадающим длинам волн.

    Эта функция принимает два набора данных: массивы длин волн и соответствующие им спектры для двух объектов,
    и выполняет операцию суммирования на основе совпадающих длин волн.

    Параметры:
        array_1 (ndarray): Массив длин волн первого объекта.
        meaning_1 (ndarray): Спектр (значения) первого объекта, соответствующий array_1.
        array_2 (ndarray): Массив длин волн второго объекта.
        meaning_2 (ndarray): Спектр (значения) второго объекта, соответствующий array_2.

    Возвращает:
        tuple: Кортеж из двух NumPy массивов:
            - array (ndarray): массив, содержащий совпадающие длины волн из array_1 и array_2.
            - meaning (ndarray): массив, содержащий сумму значений спектров (meaning_1 + meaning_2)
              для соответствующих длин волн.
    """
    array = []
    meaning = []
    for i in range(array_1.shape[0]):
        for j in range(array_2.shape[0]):
            if array_1[i] == array_2[j]:
                array.append(array_1[i])
                meaning.append(meaning_1[i] + meaning_2[j])
    return np.array(array), np.array(meaning)


#собираем за атмосферой все 4 компоненты
#принимает на вход галактические координаты
#принимает на вход дату и время наблюдения по UTC
def total_background(l, b, date, time, Sun_sp_wl = wavelenght_newguey2003, Sun_sp_fx = flux_newguey2003, V_wl = wavelenght_band_V, V_tr = trancparency_band_V, wavelenght_airglow = wavelenght_kp, intensity_airglow = intensity_kp, wavelenght_atmosphere_kp = wavelenght_modtran_kp, transparency_atmosphere_kp = trancparency_modtran_kp, venus_albedo_wl = venus_alb_wl, venus_albedo_rf = venus_alb_rf, mars_albedo_wl = mars_alb_wl, mars_albedo_rf = mars_alb_rf, jupiter_albedo_wl = jupiter_alb_wl, jupiter_albedo_rf = jupiter_alb_rf, saturn_albedo_wl = saturn_alb_wl, saturn_albedo_rf = saturn_alb_rf):
    """
    Вычисляет суммарный спектр фонового излучения для заданных галактических координат, даты и времени.

    Функция объединяет четыре компоненты фонового излучения:
    1. Зодиакальный свет.
    2. Собственное свечение атмосферы (включая ночную засветку).
    3. Спектр звезд в заданной области неба.
    4. Вклад планет Солнечной системы (Венера, Марс, Юпитер, Сатурн).

    Параметры:
        l (float): Галактическая долгота центра квадрата (в градусах).
        b (float): Галактическая широта центра квадрата (в градусах).
        date (str): Дата наблюдения в формате 'YYYY-MM-DD' (например, '2023-11-03').
        time (str): Время наблюдения в формате 'HH:MM:SS' (например, '12:00:00').
        Sun_sp_wl (ndarray, optional): Массив длин волн солнечного спектра (в нм). 
                                           По умолчанию используется `wavelenght_newguey2003`.
        Sun_sp_fx (ndarray, optional): Массив значений солнечного спектра (в фот / (сек м^2 нм)).
                                           По умолчанию используется `flux_newguey2003`.
        V_wl (ndarray, optional): Массив длин волн полосы пропускания V (в нм).
                                     По умолчанию используется `wavelenght_band_V`.
        V_tr (ndarray, optional): Массив значений прозрачности полосы пропускания V.
                                     По умолчанию используется `trancparency_band_V`.
        wavelenght_airglow (ndarray, optional): Массив длин волн для собственного свечения атмосферы (в нм).
                                                   По умолчанию используется `wavelenght_kp`.
        intensity_airglow (ndarray, optional): Массив интенсивностей собственного свечения атмосферы.
                                                  По умолчанию используется `intensity_kp`.
        wavelenght_atmosphere_kp (ndarray, optional): Массив длин волн для модели атмосферы (в нм).
                                                      По умолчанию используется `wavelenght_modtran_kp`.
        transparency_atmosphere_kp (ndarray, optional): Массив значений прозрачности атмосферы.
                                                        По умолчанию используется `trancparency_modtran_kp`.
        venus_albedo_wl (ndarray, optional): Массив длин волн спектра альбедо Венеры (в нм).
                                                По умолчанию используется `venus_alb_wl`.
        venus_albedo_rf (ndarray, optional): Массив значений спектра альбедо Венеры.
                                                По умолчанию используется `venus_alb_rf`.
        mars_albedo_wl (ndarray, optional): Массив длин волн спектра альбедо Марса (в нм).
                                               По умолчанию используется `mars_alb_wl`.
        mars_albedo_rf (ndarray, optional): Массив значений спектра альбедо Марса.
                                               По умолчанию используется `mars_alb_rf`.
        jupiter_albedo_wl (ndarray, optional): Массив длин волн спектра альбедо Юпитера (в нм).
                                                  По умолчанию используется `jupiter_alb_wl`.
        jupiter_albedo_rf (ndarray, optional): Массив значений спектра альбедо Юпитера.
                                                  По умолчанию используется `jupiter_alb_rf`.
        saturn_albedo_wl (ndarray, optional): Массив длин волн спектра альбедо Сатурна (в нм).
                                                 По умолчанию используется `saturn_alb_wl`.
        saturn_albedo_rf (ndarray, optional): Массив значений спектра альбедо Сатурна.
                                                 По умолчанию используется `saturn_alb_rf`.

    Возвращает:
        tuple: Кортеж из двух массивов:
            - wavelengths (ndarray): Массив уникальных длин волн, объединяющий все компоненты спектра (в нм).
            - spectrum (ndarray): Массив суммарных интенсивностей для каждой длины волны (в фот / (сек м^2 нм ср)).

    Примечания:
        - Функция вычисляет спектр для квадрата размером 0.1 x 0.1 градуса по галактическим координатам.
        - Для объединения спектров используется функция `sum_of_spectrums`.
        - Если планета находится вне заданного квадрата, её вклад в спектр считается равным нулю.
        - Пользователь может задать свои данные вместо стандартных значений по умолчанию.

    Зависимости:
        - `Sun_ecl_lon`: Для вычисления эклиптической долготы Солнца.
        - `galactic_to_equatorial`: Для преобразования галактических координат в эклиптические.
        - `zodiacal_spectrum`: Для вычисления спектра зодиакального света.
        - `airglow_spectrum`: Для вычисления спектра собственного свечения атмосферы.
        - `star_spectrum`: Для вычисления спектра звезд.
        - `coordinates_of_planet`: Для определения координат планет.
        - `venus_spectrum`, `mars_spectrum`, `jupiter_spectrum`, `saturn_spectrum`: Для вычисления спектров планет.
        - `sum_of_spectrums`: Для объединения спектров.
    """
    #получаем эклиптическую долготу Солнца
    lmbd_Sun = Sun_ecl_lon(date, time)
    #переводим галактические координаты в эклиптические геоцентрические
    lmbd, beta = galactic_to_equatorial(l, b)
    #получаем спектр зодиакального света (нм, фот / (м^2 сек нм ср))
    zodiac_wl, zodiac_spec = zodiacal_spectrum(lmbd, beta, lmbd_Sun, Sun_sp_wl, Sun_sp_fx, V_wl, V_tr)
    print('ФОТОНОВ ЗОДИКА:', integral(zodiac_wl, zodiac_spec))
#     return(zodiac_wl, zodiac_spec)

    #собственное свечение достаем
    airglow_wl, airglow_spec = airglow_spectrum(wavelenght_airglow, intensity_airglow, wavelenght_atmosphere_kp, transparency_atmosphere_kp)
    print('ФОТОНОВ СОБСТВЕННОГО:', integral(airglow_wl, airglow_spec))

#     return(airglow_wl, airglow_spec)
    #зод. свет и собств. свечение -- окей. Нужно допилить звездные каталоги и планеты.
    
    #звездные каталоги
    star_cat_wl = zodiac_wl
    star_cat_spec = star_spectrum(l, b, star_cat_wl)
    print('ФОТОНОВ ЗВЕЗД:', integral(star_cat_wl, star_cat_spec))
#     return star_cat_wl, star_cat_spec

    #планеты
    #Венера
    venus_l, venus_b = coordinates_of_planet('venus', date, time)
    print('Техническая проверка координат Венеры:', round(venus_l, 1), round(venus_b, 1))
    if round(venus_l, 1) == l and round(venus_b, 1) == b:
        venus_wl, venus_sp = venus_spectrum(date, time, Sun_sp_wl, Sun_sp_fx, venus_albedo_wl, venus_albedo_rf, V_wl, V_tr)
    else:
        venus_wl = zodiac_wl
        venus_sp = np.zeros(venus_wl.shape[0])
    print('ФОТОНОВ ВЕНЕРЫ:', integral(venus_wl, venus_sp))
    
    #Марс
    mars_l, mars_b = coordinates_of_planet('mars', date, time)
    print('Техническая проверка координат Марса:', round(mars_l, 1), round(mars_b, 1))
    if round(mars_l, 1) == l and round(mars_b, 1) == b:
        mars_wl, mars_sp = mars_spectrum(date, time, Sun_sp_wl, Sun_sp_fx, mars_albedo_wl, mars_albedo_rf, V_wl, V_tr)
    else:
        mars_wl = zodiac_wl
        mars_sp = np.zeros(mars_wl.shape[0])
    print('ФОТОНОВ МАРСА:', integral(mars_wl, mars_sp))
        
    #Юпитер
    jupiter_l, jupiter_b = coordinates_of_planet('jupiter', date, time)
    print('Техническая проверка координат Юпитера:', round(jupiter_l, 1), round(jupiter_b, 1))
    if round(jupiter_l, 1) == l and round(jupiter_b, 1) == b:
        jupiter_wl, jupiter_sp = jupiter_spectrum(date, time, Sun_sp_wl, Sun_sp_fx, jupiter_albedo_wl, jupiter_albedo_rf, V_wl, V_tr)
    else:
        jupiter_wl = zodiac_wl
        jupiter_sp = np.zeros(jupiter_wl.shape[0])
    print('ФОТОНОВ ЮПИТЕРА:', integral(jupiter_wl, jupiter_sp))
        
    #Сатурн
    saturn_l, saturn_b = coordinates_of_planet('saturn', date, time)
    print('Техническая проверка координат Сатурна:', round(saturn_l, 1), round(saturn_b, 1))
    if round(saturn_l, 1) == l and round(saturn_b, 1) == b:
        saturn_wl, saturn_sp = saturn_spectrum(date, time, Sun_sp_wl, Sun_sp_fx, saturn_albedo_wl, saturn_albedo_rf, V_wl, V_tr)
    else:
        saturn_wl = zodiac_wl
        saturn_sp = np.zeros(saturn_wl.shape[0])
    print('ФОТОНОВ САТУРНА:', integral(saturn_wl, saturn_sp))
        
    #теперь бы объединить эти спектры
    #делаю на основе функции sum_of_spectrums
    zod_air_wl, zod_air_sp = sum_of_spectrums(zodiac_wl, zodiac_spec, airglow_wl, airglow_spec)
    
    z_a_s_wl, z_a_s_sp = sum_of_spectrums(zod_air_wl, zod_air_sp, star_cat_wl, star_cat_spec)
    
    zas_v_wl, zas_v_sp = sum_of_spectrums(z_a_s_wl, z_a_s_sp, venus_wl, venus_sp)
    zas_vm_wl, zas_vm_sp = sum_of_spectrums(zas_v_wl, zas_v_sp, mars_wl, mars_sp)
    zas_vmj_wl, zas_vmj_sp = sum_of_spectrums(zas_vm_wl, zas_vm_sp, jupiter_wl, jupiter_sp)
    zas_vmjs_wl, zas_vmjs_sp = sum_of_spectrums(zas_vmj_wl, zas_vmj_sp, saturn_wl, saturn_sp)
    
    return zas_vmjs_wl, zas_vmjs_sp

#h --- в м
def transparency(h, zenith_angle): #на выходе дает расчитанную прозрачность
    """
    Вычисляет прозрачность атмосферы по заданной высоте наблюдателя и углу к зениту.

    Функция использует модель стандартной атмосферы США (U.S. Standard Atmosphere), описанную в Corsika,
    для расчета толщины атмосферы над наблюдателем на основе его высоты. Затем применяет зависимость
    экстинкции от длины волны, полученной с использованием MODTRAN, чтобы вычислить прозрачность.

    Параметры:
        h (float): Высота наблюдателя над уровнем моря (в метрах).
        zenith_angle (float): Угол между направлением наблюдения и вертикалью (в градусах).

    Возвращает:
        tuple: Кортеж из двух массивов:
            - wl (ndarray): Массив длин волн (в нм), для которых рассчитана прозрачность.
            - tr (ndarray): Массив значений прозрачности атмосферы для каждой длины волны.

    Примечания:
        - Толщина атмосферы вычисляется по модели U.S. Standard Atmosphere
        - Коэффициент экстинкции \( x_0 \) берется из данных MODTRAN (`x_0_modtran_us`).
        - Если высота наблюдателя выходит за пределы определения функции, возвращается `None`.

    Пример:
        >>> h = 1000  # Высота наблюдателя (метры)
        >>> zenith_angle = 30  # Угол к зениту (градусы)
        >>> wavelengths, transparency_values = transparency(h, zenith_angle)
        >>> wavelengths[:3]
        array([350., 351., 352.])
        >>> transparency_values[:3]
        array([0.999, 0.998, 0.997])

    Ссылки:
        - Corsika: Модель стандартной атмосферы США.
        - MODTRAN: Данные для коэффициента экстинкции.
    """
    h = h * 0.001 #км
    a = np.array([-186.555305, -94.919, 0.61289, 0.0, 0.01128292]) #г/см^2
    b = np.array([1222.6562, 1144.9069, 1305.5948, 540.1778, 1]) #г/см^2
    c = np.array([994186.38, 878153.55, 636143.04, 772170.16, 10**9]) #см
    c = c * 0.01 * 0.001 #км
    if h >=0 and h < 4:
        T = a[0] + b[0] * np.exp(- h / c[0])
    elif h >= 4 and h < 10:
        T = a[1] + b[1] * np.exp(- h / c[1])
    elif h >= 10 and h < 40:
        T = a[2] + b[2] * np.exp(- h / c[2])
    elif h >= 40 and h < 100:
        T = a[3] + b[3] * np.exp(- h / c[3])
    elif h >= 100 and h <= 112.8:
        T = a[4] + b[4] * np.exp(- h / c[4])
    elif h > 112.8:
        T = 0
    else:
        T = None
        print('Введенная высота наблюдателя лежит за пределами определения функции')
    
    T_angle = T / cos(zenith_angle)
    wl = wavelenght_modtran_kp
    x0 = x_0_modtran_us
    tr = np.exp(- T_angle / x_0_modtran_us)
    
    return(wl, tr)

def total_background_on_Earth(lat_obs, lon_obs, h, zenith_angle, azimuth_angle, date, time, wl_tr = [None], sp_tr = [None], Sun_sp_wl = wavelenght_newguey2003, Sun_sp_fx = flux_newguey2003, V_wl = wavelenght_band_V, V_tr = trancparency_band_V, wavelenght_airglow = wavelenght_kp, intensity_airglow = intensity_kp, wavelenght_atmosphere_kp = wavelenght_modtran_kp, transparency_atmosphere_kp = trancparency_modtran_kp, venus_albedo_wl = venus_alb_wl, venus_albedo_rf = venus_alb_rf, mars_albedo_wl = mars_alb_wl, mars_albedo_rf = mars_alb_rf, jupiter_albedo_wl = jupiter_alb_wl, jupiter_albedo_rf = jupiter_alb_rf, saturn_albedo_wl = saturn_alb_wl, saturn_albedo_rf = saturn_alb_rf):
    """
    Вычисляет суммарный спектр фонового излучения для заданных условий наблюдения на Земле
    для квадрата размером 0.1 x 0.1 градуса по галактическим координатам.

    Функция учитывает следующие компоненты фонового излучения:
    1. Зодиакальный свет.
    2. Собственное свечение атмосферы (включая ночную засветку).
    3. Спектр звезд в заданной области неба.
    4. Вклад планет Солнечной системы (Венера, Марс, Юпитер, Сатурн).

    Результат возвращается с учетом прохождения излучения через атмосферу и отображается 
    для квадрата размером 0.1 x 0.1 градуса по галактическим координатам.

    Параметры:
        lat_obs (float): Широта наблюдателя (в градусах). Должна находиться в диапазоне [-90, 90]
        lon_obs (float): Долгота наблюдателя (в градусах). Должна находиться в диапазоне [0, 360]
        h (float): Высота наблюдателя над уровнем моря (в метрах).
        zenith_angle (float): Зенитный угол направления наблюдения (в градусах). Должен находиться в диапазоне [0, 90]
        azimuth_angle (float): Азимутальный угол направления наблюдения (в градусах, от севера по часовой стрелке). Должен находиться в диапазоне [0, 360]
        date (str): Дата наблюдения в формате 'YYYY-MM-DD' (например, '2023-11-03').
        time (str): Время наблюдения в формате 'HH:MM:SS' (например, '12:00:00').
        wl_tr (ndarray, optional): Массив длин волн для прозрачности атмосферы (в нм). 
                                      По умолчанию вычисляется автоматически.
        sp_tr (ndarray, optional): Массив значений прозрачности атмосферы. 
                                      По умолчанию вычисляется автоматически.
        Sun_sp_wl (ndarray, optional): Массив длин волн солнечного спектра (в нм). 
                                          По умолчанию используется `wavelenght_newguey2003`.
        Sun_sp_fx (ndarray, optional): Массив значений солнечного спектра (в фот / (сек м^2 нм)).
                                          По умолчанию используется `flux_newguey2003`.
        V_wl (ndarray, optional): Массив длин волн полосы пропускания V (в нм).
                                     По умолчанию используется `wavelenght_band_V`.
        V_tr (ndarray, optional): Массив значений прозрачности полосы пропускания V.
                                     По умолчанию используется `trancparency_band_V`.
        wavelenght_airglow (ndarray, optional): Массив длин волн для собственного свечения атмосферы (в нм).
                                                   По умолчанию используется `wavelenght_kp`.
        intensity_airglow (ndarray, optional): Массив интенсивностей собственного свечения атмосферы.
                                                  По умолчанию используется `intensity_kp`.
        wavelenght_atmosphere_kp (ndarray, optional): Массив длин волн для модели атмосферы (в нм).
                                                      По умолчанию используется `wavelenght_modtran_kp`.
        transparency_atmosphere_kp (ndarray, optional): Массив значений прозрачности атмосферы.
                                                        По умолчанию используется `trancparency_modtran_kp`.
        venus_albedo_wl (ndarray, optional): Массив длин волн спектра альбедо Венеры (в нм).
                                                По умолчанию используется `venus_alb_wl`.
        venus_albedo_rf (ndarray, optional): Массив значений спектра альбедо Венеры.
                                                По умолчанию используется `venus_alb_rf`.
        mars_albedo_wl (ndarray, optional): Массив длин волн спектра альбедо Марса (в нм).
                                               По умолчанию используется `mars_alb_wl`.
        mars_albedo_rf (ndarray, optional): Массив значений спектра альбедо Марса.
                                               По умолчанию используется `mars_alb_rf`.
        jupiter_albedo_wl (ndarray, optional): Массив длин волн спектра альбедо Юпитера (в нм).
                                                  По умолчанию используется `jupiter_alb_wl`.
        jupiter_albedo_rf (ndarray, optional): Массив значений спектра альбедо Юпитера.
                                                  По умолчанию используется `jupiter_alb_rf`.
        saturn_albedo_wl (ndarray, optional): Массив длин волн спектра альбедо Сатурна (в нм).
                                                 По умолчанию используется `saturn_alb_wl`.
        saturn_albedo_rf (ndarray, optional): Массив значений спектра альбедо Сатурна.
                                                 По умолчанию используется `saturn_alb_rf`.

    Возвращает:
        tuple: Кортеж из двух массивов:
            - wavelengths (ndarray): Массив уникальных длин волн, объединяющий все компоненты спектра (в нм).
            - spectrum (ndarray): Массив суммарных интенсивностей для каждой длины волны (в фот / (сек м^2 нм ср)).

    Примечания:
        - Функция преобразует географические координаты наблюдателя и углы направления наблюдения 
          в галактические координаты с использованием библиотеки `astropy`.
        - Для расчета прозрачности атмосферы используется функция `transparency`, если она не передана явно.
        - Для объединения спектров используется функция `convolution`.
        - Если планета находится вне заданного квадрата, её вклад в спектр считается равным нулю.
        - Пользователь может задать свои данные вместо стандартных значений по умолчанию.

    Зависимости:
        - `astropy.coordinates.EarthLocation`: Для создания объекта местоположения наблюдателя.
        - `astropy.coordinates.AltAz`: Для представления горизонтальной системы координат.
        - `astropy.coordinates.Galactic`: Для преобразования координат в галактическую систему.
        - `transparency`: Для расчета прозрачности атмосферы.
        - `total_background`: Для расчета суммарного спектра фонового излучения.
        - `convolution`: Для учета прохождения излучения через атмосферу.
    """
    if wl_tr[0] == None and sp_tr[0] == None:
        wl_tr, sp_tr = transparency(h, zenith_angle)
    
    import astropy.units as u
    lat_obs = lat_obs * u.deg  # Широта наблюдателя
    lon_obs = lon_obs * u.deg  # Долгота наблюдателя
    h = h * u.m  # Высота над уровнем моря
    zenith_angle = zenith_angle * u.deg  # Зенитный угол (угол от зенита)
    azimuth_angle = azimuth_angle * u.deg  # Азимутальный угол (от севера по часовой стрелке)
    datetime = date + 'T' + time # Дата и время


    # Создаем объект местоположения наблюдателя
    observer_location = EarthLocation(lat=lat_obs, lon=lon_obs, height=h)


    # Определяем направление взгляда в горизонтальной системе координат
    altitude = 90 * u.deg - zenith_angle  # Вычисляем высоту как дополнение до 90 градусов
    observing_direction = AltAz(
        alt=altitude,
        az=azimuth_angle,
        location=observer_location,
        obstime=datetime,
        pressure=0  # Отключение рефракции
    )

    galactic_coords = observing_direction.transform_to(Galactic())

    l = round(galactic_coords.l.value, 1)
    b = round(galactic_coords.b.value, 1)
    print('Галактические координаты: ', l, b)

    tot_gal_wl, tot_gal_sp = total_background(l, b, date, time, Sun_sp_wl, Sun_sp_fx, V_wl, V_tr, wavelenght_airglow, intensity_airglow, wavelenght_atmosphere_kp, transparency_atmosphere_kp, venus_albedo_wl, venus_albedo_rf, mars_albedo_wl, mars_albedo_rf, jupiter_albedo_wl, jupiter_albedo_rf, saturn_albedo_wl, saturn_albedo_rf)
    
    result_wl, result_sp = convolution(tot_gal_wl, tot_gal_sp, wl_tr, sp_tr)
    
    return(result_wl, result_sp)