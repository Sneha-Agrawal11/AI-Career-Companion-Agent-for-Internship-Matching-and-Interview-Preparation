const BadgeList = ({ items, variant = "default", emptyText = "Not provided" }) => {
  if (!items || items.length === 0) {
    return <p className="muted-text">{emptyText}</p>;
  }

  return (
    <div className="badge-list">
      {items.map((item, index) => (
        <span key={`${item}-${index}`} className={`badge badge-${variant}`}>
          {item}
        </span>
      ))}
    </div>
  );
};

export default BadgeList;
