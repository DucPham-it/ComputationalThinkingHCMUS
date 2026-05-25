import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Camera, LogOut } from "lucide-react";

import { useApp } from "../hooks/useApp";
import { useAuth } from "../hooks/useAuth";
import { updateProfile as updateProfileRequest } from "../services/authService";
import { uploadAvatar } from "../services/uploadService";

const pageStyles = {
  minHeight: "calc(100vh - 140px)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "32px 16px"
};

const formStyles = {
  width: "min(100%, 760px)",
  display: "grid",
  gap: "20px"
};

const gridStyles = {
  display: "grid",
  gap: "16px",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))"
};

const labelStyles = {
  display: "grid",
  gap: "8px",
  fontWeight: 600,
  color: "var(--color-text)"
};

const statusStyles = {
  padding: "12px 16px",
  borderRadius: "12px",
  textAlign: "center",
  background: "rgba(239, 246, 255, 0.9)",
  border: "1px solid rgba(37, 99, 235, 0.16)",
  color: "var(--color-primary-dark)"
};

const submitStyles = {
  width: "100%",
  padding: "14px 18px",
  borderRadius: "16px",
  fontSize: "1rem",
  fontWeight: 700
};

const logoutStyles = {
  width: "100%",
  padding: "14px 18px",
  borderRadius: "16px",
  fontSize: "1rem",
  fontWeight: 700,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  gap: "8px"
};

function toOptionalValue(value) {
  const normalized = String(value || "").trim();
  return normalized ? normalized : null;
}

export default function ProfileSettings({ embedded = false, onSaved }) {
  const navigate = useNavigate();
  const { user, setUser, logout } = useAuth();
  const { resetAppState } = useApp();
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(user?.avatar_url || "");

  useEffect(() => {
    const token = window.localStorage.getItem("access_token");
    if (!token) {
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  useEffect(() => {
    if (!avatarFile) {
      setAvatarPreview(user?.avatar_url || "");
      return undefined;
    }

    const previewUrl = URL.createObjectURL(avatarFile);
    setAvatarPreview(previewUrl);
    return () => URL.revokeObjectURL(previewUrl);
  }, [avatarFile, user?.avatar_url]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const payload = {
      first_name: String(formData.get("first_name") || "").trim(),
      last_name: String(formData.get("last_name") || "").trim(),
      birth_date: String(formData.get("birth_date") || "").trim(),
      gender: toOptionalValue(formData.get("gender")),
      address: toOptionalValue(formData.get("address"))
    };

    try {
      const auth = await updateProfileRequest(payload);
      let nextUser = auth.user;
      if (avatarFile) {
        const avatar = await uploadAvatar(avatarFile);
        nextUser = avatar.user;
      }
      setUser(nextUser);
      onSaved?.(nextUser);
      if (!embedded) {
        navigate("/profile");
      }
    } catch (requestError) {
      setError(
        requestError?.response?.data?.detail ||
          "Profile update failed. Please check your information and try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleAvatarChange(event) {
    const file = event.target.files?.[0] || null;
    setAvatarFile(file);
  }

  function handleLogout() {
    logout();
    resetAppState();
    navigate("/login", { replace: true });
  }

  const form = (
    <form className="card" style={formStyles} onSubmit={handleSubmit}>
      <div>
        <h2>Settings</h2>
        <p>Update your account details, avatar, and profile completion fields.</p>
      </div>

      <label
        style={{
          display: "flex",
          alignItems: "center",
          gap: "16px",
          cursor: "pointer",
          fontWeight: 700,
        }}
      >
        <span
          style={{
            width: "88px",
            height: "88px",
            borderRadius: "50%",
            background: avatarPreview
              ? `url(${avatarPreview}) center/cover`
              : "var(--color-primary-soft)",
            display: "grid",
            placeItems: "center",
            color: "var(--color-primary)",
            border: "1px solid rgba(37, 99, 235, 0.18)",
            flexShrink: 0,
          }}
        >
          {avatarPreview ? null : <Camera size={28} />}
        </span>
        <span style={{ display: "grid", gap: "6px" }}>
          Avatar
          <input
            name="avatar"
            type="file"
            accept="image/png,image/jpeg,image/webp,image/gif"
            onChange={handleAvatarChange}
            disabled={isSubmitting}
          />
        </span>
      </label>

      <div style={gridStyles}>
        <label style={labelStyles}>
          First Name
          <input
            name="first_name"
            type="text"
            placeholder="Nguyen"
            autoComplete="given-name"
            defaultValue={user?.first_name || ""}
            required
          />
        </label>

        <label style={labelStyles}>
          Last Name
          <input
            name="last_name"
            type="text"
            placeholder="An"
            autoComplete="family-name"
            defaultValue={user?.last_name || ""}
            required
          />
        </label>

        <label style={labelStyles}>
          Birth Day
          <input
            name="birth_date"
            type="date"
            autoComplete="bday"
            defaultValue={user?.birth_date || ""}
            required
          />
        </label>

        <label style={labelStyles}>
          Gender
          <select name="gender" defaultValue={user?.gender || ""}>
            <option value="">Prefer not to say</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
          </select>
        </label>
      </div>

      <label style={labelStyles}>
        Address
        <textarea
          name="address"
          rows={3}
          placeholder="123 Nguyen Trai, District 5, Ho Chi Minh City"
          autoComplete="street-address"
          defaultValue={user?.address || ""}
        />
      </label>

      <button className="btn-primary" style={submitStyles} disabled={isSubmitting}>
        {isSubmitting ? "Saving profile..." : "Save Profile"}
      </button>

      <button
        type="button"
        className="btn-outline"
        style={logoutStyles}
        onClick={handleLogout}
        disabled={isSubmitting}
      >
        <LogOut size={18} />
        Logout
      </button>

      <Link
        to="/admin"
        className="btn-outline"
        style={{ ...logoutStyles, textDecoration: "none" }}
      >
        Admin console / request admin
      </Link>

      {error ? <div style={statusStyles}>{error}</div> : null}
    </form>
  );

  if (embedded) {
    return form;
  }

  return <section style={pageStyles}>{form}</section>;
}
