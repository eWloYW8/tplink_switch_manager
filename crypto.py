def security_encode(input_str, key1, key2):
    k = key2
    result = ""
    len_input = len(input_str)
    len_key1 = len(key1)
    len_k = len(k)
    h = len_input if len_input > len_key1 else len_key1
    
    for g in range(h):
        l_val = 187
        i_val = 187
        if g >= len_input:
            i_val = ord(key1[g])
        elif g >= len_key1:
            l_val = ord(input_str[g])
        else:
            l_val = ord(input_str[g])
            i_val = ord(key1[g])
        index = (l_val ^ i_val) % len_k
        result += k[index]
    return result

def get_encrypted_password(password):
    val_b = "RDpbLfCPsJZ7fiv"
    val_a = "yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW"
    return security_encode(password, val_b, val_a)
