import os
import puttykeys

def convert_ppk(ppk_path, out_path):
    print(f"Loading {ppk_path}...")
    try:
        with open(ppk_path, "r") as f:
            raw_ppk = f.read()
        
        openssh_key = puttykeys.ppkraw_to_openssh(raw_ppk)
        
        with open(out_path, "wb") as f:
            if isinstance(openssh_key, str):
                f.write(openssh_key.encode("utf-8"))
            else:
                f.write(openssh_key)
        os.chmod(out_path, 0o600)
        print(f"Successfully converted to {out_path}")
    except Exception as e:
        print(f"Error converting {ppk_path}: {e}")

if __name__ == "__main__":
    convert_ppk("/home/extreme/ssh/ubuntu_private.ppk", "/home/extreme/ssh/ubuntu_id_ed25519")
    convert_ppk("/home/extreme/ssh/jsappuser_private.ppk", "/home/extreme/ssh/jsappuser_id_ed25519")
