import { useEffect, useState } from "react";
import { CheckCircle2, ShieldCheck, XCircle } from "lucide-react";

import Error from "../components/common/Error";
import LoadingSpinner from "../components/common/LoadingSpinner";
import Section from "../components/common/Section";
import { useAuth } from "../hooks/useAuth";
import {
  applyForAdminAccess,
  approveAdminMember,
  approvePlaceRequest,
  fetchAdminMembers,
  fetchAdminProfile,
  fetchPlaceRequests,
  rejectAdminMember,
  rejectPlaceRequest,
} from "../services/adminService";

function formatRequestTitle(item) {
  return `${item.request_type.toUpperCase()} #${item.id}: ${item.title || item.address_text || `Place ${item.target_place_id || item.place_id || ""}`}`;
}

export default function Admin() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [members, setMembers] = useState([]);
  const [requests, setRequests] = useState([]);
  const [statusFilter, setStatusFilter] = useState("pending");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const isApprovedAdmin = profile?.status === "approved" || user?.is_admin;

  async function loadAdminData(nextStatus = statusFilter) {
    try {
      setLoading(true);
      setError("");
      const profileResponse = await fetchAdminProfile();
      setProfile(profileResponse);

      if (profileResponse.status === "approved" || user?.is_admin) {
        const [memberItems, requestItems] = await Promise.all([
          fetchAdminMembers(),
          fetchPlaceRequests(nextStatus),
        ]);
        setMembers(memberItems);
        setRequests(requestItems);
      }
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || "Admin data is unavailable.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAdminData(statusFilter);
  }, [statusFilter]);

  async function handleApply() {
    try {
      setMessage("");
      const nextProfile = await applyForAdminAccess();
      setProfile(nextProfile);
      setMessage("Admin access request submitted.");
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || "Could not submit admin request.");
    }
  }

  async function handlePlaceDecision(item, decision) {
    try {
      setMessage("");
      if (decision === "approve") {
        await approvePlaceRequest(item.id);
        setMessage(`Approved request #${item.id}.`);
      } else {
        await rejectPlaceRequest(item.id);
        setMessage(`Rejected request #${item.id}.`);
      }
      await loadAdminData(statusFilter);
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || "Could not review this request.");
    }
  }

  async function handleAdminDecision(member, decision) {
    try {
      setMessage("");
      if (decision === "approve") {
        await approveAdminMember(member.user_id);
        setMessage(`Approved admin user #${member.user_id}.`);
      } else {
        await rejectAdminMember(member.user_id);
        setMessage(`Rejected admin user #${member.user_id}.`);
      }
      await loadAdminData(statusFilter);
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || "Could not update admin member.");
    }
  }

  if (loading) {
    return <LoadingSpinner message="Loading admin console..." />;
  }

  return (
    <div style={{ display: "grid", gap: "24px" }}>
      <Section title="Admin Console" subtitle="Approve user-submitted place additions, edits, and delete requests.">
        <div className="card" style={{ display: "grid", gap: "12px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
            <ShieldCheck size={22} color="var(--color-primary)" />
            <strong>Status:</strong>
            <span>{profile?.status || "not requested"}</span>
          </div>

          {!isApprovedAdmin ? (
            <button className="btn-primary" onClick={handleApply} style={{ padding: "12px 18px", borderRadius: "14px", fontWeight: 800 }}>
              Request admin access
            </button>
          ) : null}

          {message ? (
            <p style={{ margin: 0, padding: "12px", borderRadius: "12px", background: "#ecfdf5", color: "#047857", fontWeight: 700 }}>
              {message}
            </p>
          ) : null}
        </div>
      </Section>

      {error ? <Error message={error} /> : null}

      {isApprovedAdmin ? (
        <>
          <Section title="Place Requests" subtitle="Review pending or historical user proposals.">
            <div style={{ display: "grid", gap: "16px" }}>
              <div className="card" style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
                <strong>Filter</strong>
                <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} style={{ maxWidth: "220px" }}>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                  <option value="">All</option>
                </select>
              </div>

              {requests.length ? requests.map((item) => (
                <article key={item.id} className="card" style={{ display: "grid", gap: "12px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "12px", flexWrap: "wrap" }}>
                    <h3 style={{ margin: 0 }}>{formatRequestTitle(item)}</h3>
                    <strong style={{ color: "var(--color-primary)" }}>{item.status}</strong>
                  </div>
                  <p style={{ margin: 0 }}>{item.request_note || item.descriptions || "No request note."}</p>
                  <p style={{ margin: 0, color: "var(--color-text-soft)" }}>
                    Requested by {item.requester_name || `user #${item.requester_user_id}`} at {item.created_at || "unknown time"}
                  </p>
                  {item.review_content ? (
                    <p style={{ margin: 0 }}>
                      Review: <strong>{item.review_rating || "N/A"}/5</strong> - {item.review_content}
                    </p>
                  ) : null}
                  {item.place_image_urls?.length ? (
                    <p style={{ margin: 0 }}>Place images: {item.place_image_urls.length}</p>
                  ) : null}
                  {item.status === "pending" ? (
                    <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
                      <button className="btn-primary" onClick={() => handlePlaceDecision(item, "approve")} style={{ padding: "10px 14px", borderRadius: "12px", fontWeight: 800 }}>
                        <CheckCircle2 size={16} style={{ marginRight: "6px" }} />
                        Approve
                      </button>
                      <button className="btn-outline" onClick={() => handlePlaceDecision(item, "reject")} style={{ padding: "10px 14px", borderRadius: "12px", fontWeight: 800 }}>
                        <XCircle size={16} style={{ marginRight: "6px" }} />
                        Reject
                      </button>
                    </div>
                  ) : null}
                </article>
              )) : (
                <div className="card">No place requests for this filter.</div>
              )}
            </div>
          </Section>

          <Section title="Admin Members" subtitle="Approve or reject pending admin accounts.">
            <div style={{ display: "grid", gap: "12px" }}>
              {members.length ? members.map((member) => (
                <div key={member.user_id} className="card" style={{ display: "flex", justifyContent: "space-between", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
                  <div>
                    <strong>{member.user_name || `User #${member.user_id}`}</strong>
                    <p style={{ margin: "4px 0 0 0" }}>{member.email || "No email"} - {member.status}</p>
                  </div>
                  {member.status === "pending" ? (
                    <div style={{ display: "flex", gap: "8px" }}>
                      <button className="btn-primary" onClick={() => handleAdminDecision(member, "approve")}>Approve</button>
                      <button className="btn-outline" onClick={() => handleAdminDecision(member, "reject")}>Reject</button>
                    </div>
                  ) : null}
                </div>
              )) : (
                <div className="card">No admin members yet.</div>
              )}
            </div>
          </Section>
        </>
      ) : null}
    </div>
  );
}

